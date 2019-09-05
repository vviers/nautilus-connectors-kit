import click
import config
import os
import logging
import httplib2

import datetime

from itertools import chain

from googleapiclient import discovery
from googleanalytics import account
from oauth2client import client, GOOGLE_REVOKE_URI

from lib.commands.command import processor
from lib.readers.reader import Reader
from lib.utils.args import extract_args
from lib.utils.retry import retry
from lib.streams.json_stream import JSONStream



DISCOVERY_URI = "https://analyticsreporting.googleapis.com/$discovery/rest"


@click.command(name="read_ga")
@click.option("--ga-access-token", default=None)
@click.option("--ga-refresh-token", required=True)
@click.option("--ga-client-id", required=True)
@click.option("--ga-client-secret", required=True)
@click.option("--ga-view-id", default= [], multiple=True)
@click.option("--ga-account-id", default=None)
@click.option("--ga-metric", multiple=True)
@click.option("--ga-dimension", multiple=True)
@click.option(
    "--ga-date-range", nargs=2, type=click.DateTime(), multiple=True, default=None
)
@click.option("--ga-day-range",   type=click.Choice(['PREVIOUS_DAY','LAST_30_DAYS' ,'LAST_7_DAYS','LAST_90_DAYS']), default = None)
@processor()
def ga(**kwargs):
    # Should handle valid combinations dimensions/metrics in the API
    return GaReader(**extract_args("ga_", kwargs))


class GaReader(Reader):
    def __init__(self, access_token, refresh_token, client_secret, client_id, **kwargs):
        credentials = client.GoogleCredentials(
            access_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            token_expiry=None,
            token_uri="https://accounts.google.com/o/oauth2/token",
            user_agent=None,
            revoke_uri=GOOGLE_REVOKE_URI,
        )

        http = credentials.authorize(httplib2.Http())
        credentials.refresh(http)
        # self.client_v3 = discovery.build("analytics", "v3", http=http)
        self.client_v4 = discovery.build(
            "analytics",
            "v4",
            http=http,
            cache_discovery=False,
            discoveryServiceUrl=DISCOVERY_URI,
        )
        self.client_v3 = discovery.build('analytics', 'v3', http=http)
        self.kwargs = kwargs
        # get cred-related accounts (not in a function to preserve homogenity with other connectors)
        accounts_infos = self.client_v3.management().accounts().list().execute()['items']
        account_id = self.kwargs.get("account_id")
        if (account_id):
            accounts_infos = [acc_inf for acc_inf in accounts_infos if acc_inf['id'] == account_id]
        if (accounts_infos == []):
           raise Exception('account_id {} not found'.format(account_id))
        
        self.accounts = [account.Account(raw, self.client_v3, credentials) for raw in  accounts_infos] 
   

    def get_accounts(self):
        accounts_infos = self.client_v3.management().accounts().list().execute()['items']
        account_id = self.kwargs.get("account_id")
        if (account_id):
            accounts_infos = [acc_inf for acc_inf in accounts_infos if acc_inf['id'] == str(account_id)]
        if (accounts_infos == []):
           raise Exception('account_id {} not found'.format(account_id))
        accounts = [account.Account(raw, self.client_v3, self.credentials) for raw in   accounts_infos] 
        return accounts

    def get_acc_propeties_ids(self, account):
        return [p.id for p in account.webproperties]

    
    def get_acc_view_ids(self, account):
        properties_ids = self.get_acc_propeties_ids(account)
        flatten = lambda l: [item for sublist in l for item in sublist]
        all_profiles = flatten([
            self.client_v3.management().profiles().list(accountId=account.id,webPropertyId= pid).execute()
            for pid in properties_ids
            ])
        return [p.id for p in all_profiles]

    def get_view_ids(self):
        view_ids = self.kwargs.get("view_id") 
        if (view_ids == []):
            flatten = lambda l: [item for sublist in l for item in sublist]
            return flatten([self.get_acc_view_ids(account) for account in self.accounts])
        else:
            return view_ids

    
    def get_days_delta(self):
        days_range = self.kwargs.get("day_range")
        if days_range == 'PREVIOUS_DAY':
            days_delta = 1
        elif days_range == 'LAST_7_DAYS':
            days_delta = 7
        elif days_range == 'LAST_30_DAYS':
            days_delta = 30
        elif days_range == 'LAST_90_DAYS':
            days_delta = 90
        else:
            raise Exception("{} is not handled by the reader".format(days_range))
        return days_delta

    def get_date_ranges(self):
        date_ranges = self.kwargs.get("date_range")
        days_range = self.kwargs.get("day_range")
        if date_ranges:
            starts = [date_range[0] for date_range in date_ranges]
            idxs = sorted(range(len(starts)), key=lambda k: starts[k])
            date_ranges_sorted = [
                {"startDate": date_ranges[idx][0].strftime("%Y-%m-%d"), "endDate": date_ranges[idx][1].strftime("%Y-%m-%d")}
                for idx in idxs
            ]
            assert (
                len(
                    [el for el in date_ranges_sorted if el["startDate"] > el["endDate"]]
                )
                == 0
            ), "date start should be inferior to date end"
            return date_ranges_sorted
        elif  days_range:
            days_delta = self.get_days_delta()
            d2 = datetime.datetime.now().date()
            d1 = d2 - datetime.timedelta(days = days_delta)
            return [{"startDate": d1.strftime("%Y-%m-%d"), "endDate": d2.strftime("%Y-%m-%d")}]
        else:
            return []

    def get_report_requests(self):
        view_ids = self.get_view_ids()
        date_ranges = self.get_date_ranges()

        report_requests = [
            {
                "viewId": view_id,
                "metrics": [
                    {"expression": val} for val in self.kwargs.get("metric", [])
                ],
                "dimensions": [
                    {"name": val} for val in self.kwargs.get("dimension", [])
                ],
            }
            if (len(date_ranges) == 0)
            else {
                "dateRanges": date_ranges,
                "viewId": view_id,
                "metrics": [
                    {"expression": val} for val in self.kwargs.get("metric", [])
                ],
                "dimensions": [
                    {"name": val} for val in self.kwargs.get("dimension", [])
                ],
            }
            for view_id in view_ids
        ]
        return report_requests

    @retry
    def _run_query(self):
        body = {"reportRequests": self.get_report_requests()}
        results = self.client_v4.reports().batchGet(body=body).execute()
        return results

    def _format_record(self, row, idx_view, reports):
        dimensions_names = reports[idx_view]["columnHeader"]["dimensions"]
        row["dimensions_names"] = dimensions_names
        metrics_infos = reports[idx_view]["columnHeader"]["metricHeader"][
            "metricHeaderEntries"
        ]
        row["metrics_infos"] = metrics_infos
        row["view_id"] =self.get_view_ids()[idx_view]
        return row

    def read(self):

        results = self._run_query()

        def result_generator(idx_view):
            for row in results["reports"][idx_view]["data"]["rows"]:
                yield self._format_record(row, idx_view, results["reports"])
        view_ids = self.get_view_ids()
        for idx_view in range(len(view_ids)):
            yield JSONStream('result_view_'+ str(view_ids[idx_view]), result_generator(idx_view))
        
# NCK Readers

Each reader role is to read data from external source and transform it into a Stream understable format to be written on GCS and BQ thanks to the corresponding writers.

## Step to create a new Reader

1. Create python module following naming nomenclature ``` [command]_reader.py ```
2. Implement `read` method
3. Create click command with required options
4. Reference click command into [commands list](./__init__.py)
5. Update current README.md


## Facebook Reader

- Example

The following command retrieves some insights of every Ads in the Facebook account <ACCOUNT_ID> thanks to
a Facebook App whose access_token is <ACCESS_TOKEN>.

```
python nck/entrypoint.py read_facebook --facebook-access-token <ACCESS_TOKEN> --facebook-ad-object-id <ACCOUNT_ID> --facebook-breakdown gender --facebook-level ad --facebook-start-date 2019-01-01 --facebook-end-date 2019-01-01 --facebook-field date_start --facebook-field date_stop --facebook-field account_currency --facebook-field account_id --facebook-field account_name --facebook-field ad_id --facebook-field ad_name --facebook-field adset_id --facebook-field adset_name --facebook-field campaign_id --facebook-field campaign_name --facebook-field clicks --facebook-field impressions --facebook-desired-field date_start --facebook-desired-field date_stop --facebook-desired-field account_name --facebook-desired-field account_id --facebook-desired-field ad_id --facebook-desired-field ad_namefacebook-desired-field clicks --facebook-desired-field impressions write_console
```

The report below is the output of the command. You can easily store it in GCS or Biquery thanks to the corresponding
writers([GCS writer](../writers/gcs_writer.py), [BQ writer](../writers/bigquery_writer.py)):
```
{
  "date_start": "2019-01-05",
  "date_stop": "2019-01-05",
  "account_name": "example_name"
  "account_id": "0000000000"
  "ad_id": "00000000000",
  "ad_name": "example_name",
  "clicks": "1",
  "impressions": "100"
}
```
See the [documentation here](https://developers.facebook.com/docs/marketing-api/insights/#marketing-api-quickstart "Create a Facebook App")
to create a Facebook App and an access token.

- Parameters of the Facebook Readers

| --facebook-app-id | --facebook-app-secret | --facebook-access-token | --facebook-ad-object-id | --facebook-ad-object-type | --facebook-breakdown | --facebook-action-breakdown | --facebook-ad-insights | --facebook-level | --facebook-time-increment | --facebook-field | --facebook-desired-field | --facebook-start-date | --facebook-end-date | --facebook-date-preset | --facebook-request-date
|:-----------------:|:---------------------:|:-----------------------:|:-----------------------:|:-------------------------:|:--------------------:|:---------------------------:|:----------------------:|:-------------------:|:-------------------------:|:----------------:|:------------------------:|:---------------------:|:-------------------:|:----------------------:|:----------------------:|
|Facebook App ID |Facebook App ID| Facebook App access token|Object ID to request (account ID, campaign ID, ...)|Object type (account, campaign, ...)|List of breakdowns for the request|List of action-breakdowns for the request|If set to true, request insights|Represents the granularity of result|Time increment|List of fields to request|Desired fields in the output report |Start date of period|End date of period|Preset period|If set to true, the date of the request will appear in the report

See the documents below for a better understanding of the parameters:
- [Facebook API Insights documentation](https://developers.facebook.com/docs/marketing-api/insights)
- [API Reference for Ad Insights](https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights/)
- [Available Fields for Nautilus](../helpers/facebook_helper.py)


## Google Readers

### Authentication

You can authenticate to most of the readers of the google 
suite following the same schema. You'll need to generate a **refresh token** to connect
via the oAuth flow. A full script to do this can be found here:

[Refresh token generator](https://github.com/artefactory/Refresh-token-generator-for-google-oauth)


### Google Ads Reader

#### How to obtain Credentials


Using the Google Ads API requires four things:
- A developer token (Generated at a company level - one per company -, takes around 2 days to be approved by Google) which can be completely independant from the Google Ads Account you will be calling (though you need a Manager Google Ads Account to request a token for your company)

- OAuth2 credentials: <CLIENT_ID> and <CLIENT_SECRET>

- A refresh token, created with the email address able to access to all the Google Ads Account you will be calling

- The ID of the GAds Accounts <CLIENT_CUSTOMER_ID> you will be reading from (XXX-XXX-XXXX numbers, written right next to your Account Name)

See the [documentation here](https://developers.google.com/adwords/api/docs/guides/signup "Sign Up for Google Ads API")
to apply for access if your Company does not already have a developer token (granting you the right to use the API).

See the [documentation here](https://developers.google.com/adwords/api/docs/guides/first-api-call "Make your first API call")
to set-up your OAuth2 credentials and refresh token specifically for your Google Ads Accounts.


#### Which Reports and Metrics are available in the API

The list of available reports for the API, and the associated metrics, can be [found here](https://developers.google.com/adwords/api/docs/appendix/reports#available-reports "Report Types")

#### Simple API call example

- Call Example


The following command retrieves insights about the Ads of *my_first_campaign* and *my_second_campaign* in the Google Ads Account <CLIENT_CUSTOMER_ID> thanks to
your company <DEVELOPER_TOKEN>, and your <CLIENT_ID>, <CLIENT_SECRET> and <REFRESH_TOKEN> with the necessary permissions to access your Accounts.

```
python nck/entrypoint.py read_googleads --googleads-developer-token <DEVELOPER_TOKEN> --googleads-client-id <CLIENT_ID> --googleads-client-secret <CLIENT_SECRET> --googleads-refresh-token <REFRESH_TOKEN> --googleads-client-customer-id <XXX-XXX-XXXX CLIENT_CUSTOMER_ID> --googleads-report-type AD_PERFORMANCE_REPORT --googleads-date-range-type LAST_7_DAYS --googleads-field CampaignName --googleads-field AdGroupName --googleads-field Headline --googleads-field Date --googleads-field Impressions --googleads-report-filter "{'field':'CampaignName','operator':'IN','values':['my_first_campaign','my_second_campaign']}" 
```

*If it doesn't work, try to* `export PYTHONPATH="."` *in the nautilus-connector-kit folder (to be sure Python is reading correctly)*
*If you want the output to be printed in your console, add* `write_console` *at the end of your command (see writers for more details)*

- Parameters of the GoogleAds Readers


| --googleads-developer-token | --googleads-client-id | --googleads-client-secret | --googleads-refresh-token | --googleads-manager-id | --googleads-client-customer-id  | --googleads-report-name | --googleads-report-type | --googleads-date-range-type | --googleads-start-date | --googleads-end-date | --googleads-field | --googleads-report-filter | --googleads-include-zero-impressions | --googleads-filter-on-video-campaigns | --googleads-include-client-customer-id |
|:-----------------:|:---------------------:|:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:|:--------------------:|:---------------------------:|:----------------------:|:-------------------:|:-------------------------:|:----------------:|:------------------------:|:------------------------:|:------------------------:|:------------------------:|
|Company Developer token for Google Ads API |OAuth2 ID| OAuth2 Secret|Refresh token for OAuth2|Manager_Account_ID (XXX-XXX-XXXX identifier) (optional)|GAds_Account_ID (ignored if a manager account ID was given)|Optional Name for your output stream ("Custom Report" by default)|Type of Report to be called|Type of Date Range to apply (if "CUSTOM_RANGE", a min and max date must be specified) |Start Date for "CUSTOM_RANGE" date range (optional)|End Date for "CUSTOM_RANGE" date range (optional)|List of fields to request |Filter to apply on a chosen field (Dictionary as String "{'field':,'operator':,'values':}")|Boolean specifying whether or not rows with zero impressions should be included in report| Boolean used to filter on Video Campaigns only (require CampaignId to be listed as a field) | Boolean used to add "AccountId" as a field in the output stream * |

\* *AccountId is not available in the API but is known since it's a requirement to call the API (= client customer ID)*

See the documents below for a better understanding of the parameters:
- [Google Ads API Reporting Basics](https://developers.google.com/adwords/api/docs/guides/reporting#create_a_report_definition)
- [Possible Date Ranges](https://developers.google.com/adwords/api/docs/guides/reporting#date_ranges)


### Google Search Console Reader

#### How to obtain Credentials

Using the Google Search Console API requires three main parameters:
- OAuth2 credentials: <CLIENT_ID> and <CLIENT_SECRET>

- A refresh token, created with the email address able to access to your Google Search Console Account.

- The URLs whose performance you want to see.

See the [documentation here](https://developers.google.com/webmaster-tools/search-console-api-original/v3/prereqs "Search Console API")
to see an Overview of the Search Console API.


#### Search Analytics

The list of available dimensions and metrics in the API can be [found here](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query "Search Analytics")

#### Simple API call example

- Call Example

The following command retrieves insights about the URL <SITE_URL> thanks to your company <CLIENT_ID> and <REFRESH_TOKEN> 
with the necessary permissions to access your Accounts.

```
python nck/entrypoint.py read_search_console --search-console-client-id <CLIENT_ID> --search-console-refresh-token <REFRESH_TOKEN> --search-console-site-url <SITE_URL> --search-console-dimensions country --search-console-dimensions device --search-console-start-date 2020-01-01 --search-console-end-date 2020-01-01 write_console 
```

- Parameters of the Google Search Console Readers

| --search-console-client-id | --search-console-client-secret | --search-console-access-token | --search-console-refresh-token | --search-console-dimensions | --search-console-site-url  | --search-console-start-date | --search-console-end-date | --search-console-date-column | --search-console-row-limit |
|:-----------------:|:---------------------:|:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:|:--------------------:|:---------------------------:|:----------------------:|:----------------------:|
|OAuth2 ID| OAuth2 Secret| Access token | Refresh token for OAuth2 | [Dimensions to request](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query#dimensionFilterGroups.filters.dimension) |Site URL whose performance you want to request| Start Date for the request | End Date for the request | If true, include date column in the report | Row number by report page |

See the documents below for a better understanding of the parameters:
- [Google Search Console API](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query)


### Search Ads 360 Reader (SA360)

#### How to obtain Credentials

Using the Search Ads API requires two things:

- OAuth2 credentials: <CLIENT_ID> and <CLIENT_SECRET>

- A refresh token, created with the email address able to access to all the Search Ads 360 Account you will be calling

See the [documentation here](https://developers.google.com/search-ads/v2/authorizing "SA360 Authentication")
to set-up your OAuth2 credentials and refresh token specifically for Search Ads 360 Reporting.


#### Which Reports and Metrics are available in the API

The list of available reports for the API, and the associated metrics, can be [found here](https://developers.google.com/search-ads/v2/report-types "Report Types")

#### Simple API call example

- Call Example


The following command retrieves insights about the Ads in the Search Ads 360 Account <ADVERTISER_ID> from the agency <AGENCY_ID> thanks to
your <CLIENT_ID>, <CLIENT_SECRET> and <REFRESH_TOKEN> with the necessary permissions to access your Accounts.

```
python nck/entrypoint.py read_sa360 --sa360-client-id <CLIENT_ID> --sa360-client-secret <CLIENT_SECRET> --sa360-refresh-token <REFRESH_TOKEN> --sa360-agency-id <AGENCY_ID> --sa360-advertiser-id <ADVERTISER_ID> --sa360-report-type keyword --sa360-column date --sa360-column impr --sa360-column clicks --sa360-start-date 2020-01-01 --sa360-end-date 2020-01-01 
```

*If it doesn't work, try to* `export PYTHONPATH="."` *in the nautilus-connector-kit folder (to be sure Python is reading correctly)*
*If you want the output to be printed in your console, add* `write_console` *at the end of your command (see writers for more details)*


- Parameters of the SA360 Reader

| CLI option | Documentation |
| ---------- | ------------- |
|`--sa360-access-token` | (Optional) Access token |
|`--sa360-client-id` | OAuth2 ID |
|`--sa360-client-secret` | OAuth2 ID Secret |
|`--sa360-refresh-token` | Refresh token |
|`--sa360-agency-id` | Agency ID to request in SA360 |
|`--sa360-advertiser-id` | (Optional) Advertiser ids to request. If not provided, every advertiser of the agency will be requested|
|`--sa360-report-name` | (Optional) Name of the output report |
|`--sa360-report-type` | Type of the report to request. List [here](https://developers.google.com/search-ads/v2/report-types)|
|`--sa360-column` | Dimensions and metrics to request in the report |
|`--sa360-saved-column` | (Optional) Saved columns to report. See [documentation](https://developers.google.com/search-ads/v2/how-tos/reporting/saved-columns)|
|`--sa360-start-date` | Start date of the period to request |
|`--sa360-end-date` | End date of the period to request |

See the documents below for a better understanding of the parameters:
- [SA360 Reporting](https://developers.google.com/search-ads/v2/how-tos/reporting)


## Yandex readers

For now, there is only one Yandex API you can access through Nautilus connectors: [Direct API](https://tech.yandex.com/direct/).
This API allows you to collect display metrics.

### Access Yandex Direct API

In order to access Yandex Direct API, you need two accounts: an advertiser account and a developer account.
Here is the process:

1. Create a developer account if you don't already have one. Click on the *Get started* button on this [page](https://direct.yandex.com/).
2. Create and register an app that will access Yandex Direct API via [Yandex OAuth](https://oauth.yandex.com/client/new).
3. Keep app client id safe. Log in with your advertiser account and [give permission to the app to access your data](https://tech.yandex.com/oauth/doc/dg/tasks/get-oauth-token-docpage/).
4. Store your token very carefully.
5. Log out and log in as a developer and [ask permission to access Yandex Direct API](https://direct.yandex.com/registered/main.pl?cmd=apiSettings) (ask for Full access). Fill in the form.
6. Wait for Yandex support to reply but it should be within a week.

### Yandex campaign reader

[Official documentation](https://tech.yandex.com/direct/doc/ref-v5/campaigns/get-docpage/)

#### Quickstart

If you want to quickly get to the point, here is a simple command that get the daily budget for all your campaigns.

```bash
python nck/entrypoint.py read_yandex_campaigns --yandex-token <TOKEN> --yandex-field-name Id --yandex-field-name Name --yandex-field-name DailyBudget write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

| CLI option | Documentation |
| ---------- | ------------- |
| `--yandex-token` | Bear token that allows you to authenticate to the API |
| `--yandex-campaign-id` | (Optional) Selects campaigns with the specified IDs. |
| `--yandex-campaign-state` | (Optional) Selects campaigns with the specified [states](https://tech.yandex.com/direct/doc/dg/objects/campaign-docpage/#status). |
| `--yandex-campaign-status` | (Optional) Selects campaigns with the specified [statuses](https://tech.yandex.com/direct/doc/dg/objects/campaign-docpage/#status). |
| `--yandex-campaign-payment-status` | (Optional) Selects campaigns with the specified payment [statuses](https://tech.yandex.com/direct/doc/dg/objects/campaign-docpage/#status). |
| `--yandex-field-name` | Parameters to get that are common to all types of campaigns. |

### Yandex statistics reader

[Official documentation](https://tech.yandex.com/direct/doc/reports/reports-docpage/)

#### Quickstart

The command below gives you a performance report for all your campaigns and since the beginning.

```bash
python nck/entrypoint.py read_yandex_statistics --yandex-token <TOKEN> --yandex-report-type AD_PERFORMANCE_REPORT --yandex-field-name AdFormat --yandex-field-name AdId --yandex-field-name Impressions --yandex-include-vat True --yandex-report-language en --yandex-field-name AdGroupName --yandex-field-name AdGroupId --yandex-field-name AdNetworkType --yandex-field-name CampaignId --yandex-field-name CampaignName --yandex-field-name CampaignType --yandex-field-name Date --yandex-field-name Device --yandex-field-name Clicks --yandex-field-name Conversions --yandex-field-name Cost --yandex-date-range ALL_TIME write_console
```

Didn't work? See [troubleshooting](#troubleshooting) section.

#### Parameters

Detailed version [here](https://tech.yandex.com/direct/doc/reports/spec-docpage/).

| CLI option | Documentation |
| ---------- | ------------- |
| `--yandex-token` | Bear token that allows you to authenticate to the API |
| `--yandex-report-language` | (Optional) Language of the report. See all options [here](https://tech.yandex.com/direct/doc/dg/concepts/headers-docpage/#headers__accept-language). |
| `--yandex-filter` | (Optional) Filters on a particular field. |
| `--yandex-max-rows` | (Optional) The maximum number of rows in the report. |
| `--yandex-field-name` | Information you want to collect. Complete list [here](https://tech.yandex.com/direct/doc/reports/fields-list-docpage/). |
| `--yandex-report-type` | Type of report. Linked to the fields you want to select. |
| `--yandex-date-range` | List [here](https://tech.yandex.com/direct/doc/reports/period-docpage/). |
| `--yandex-include-vat` | Adds VAT to your expenses if set to `True`|
| `--yandex-date-start` | (Optional) Selects data on a specific period of time. Combined with `--yandex-date-stop` and  `--yandex-date-range` set to `CUSTOM_DATE`. |
| `--yandex-date-stop` | (Optional) Selects data on a specific period of time. Combined with `--yandex-date-start` and  `--yandex-date-range` set to `CUSTOM_DATE`. |

### Troubleshooting

You encountered and you don't know what 's going on. You may find an answer in the troubleshooting guide below.

1. **Have you install NCK dependencies?** In order to run NCK, you need to install all dependencies. First create a [virtual environment](https://docs.python.org/3/library/venv.html) and then run `pip install -r requirements.txt`.
2. **Have you set `PYTHONPATH` environment variable to the root of NCK folder?**
3. **Have you checked logs?** The code has been implmented so that every error is logged. For example, if you did not provide a valid token, you will see something like ```Invalid request.
{'error': {'error_code': '53', 'request_id': '8998435864716615689', 'error_string': 'Authorization error', 'error_detail': 'Invalid OAuth token'}}```. If you misspelled a field, you will get a message like this one: ```Error: Invalid value for "--yandex-field-name"```.

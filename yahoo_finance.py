from lxml import html
import requests
from time import sleep
import json
import argparse
from collections import OrderedDict
from time import sleep

## ref: https://www.scrapehero.com/scrape-yahoo-finance-stock-market-data/
## ref: https://gist.github.com/scrapehero/516fc801a210433602fe9fd41a69b496

def parse(ticker):
    # url = "http://finance.yahoo.com/quote/%s?p=%s" % (ticker, ticker)
    url = "https://finance.yahoo.com/quote/%s?p=%s" % (ticker, ticker)
    # response = requests.get(url, verify=False)
    response = requests.get(url)
    print("Parsing %s" % (url))
    sleep(4)
    parser = html.fromstring(response.text)
    # summary_table = parser.xpath('//div[contains(@data-test,"summary-table")]//tr')
    summary_table = parser.xpath('//*[@id="quote-summary"]/div/table/tbody/tr')
    ## xpath: //*[@id="quote-summary"]/div[1]/table/tbody/tr[2]
    ## selector: #quote-summary > div.D\28 ib\29.W\28 1\2f 2\29.Bxz\28 bb\29.Pend\28 12px\29.Va\28 t\29.ie-7_D\28 i\29.smartphone_D\28 b\29.smartphone_W\28 100\25 \29.smartphone_Pend\28 0px\29.smartphone_BdY.smartphone_Bdc\28 \24 c-fuji-grey-c\29 > table > tbody > tr:nth-child(2)
    ## outerHTML: <tr class="Bxz(bb) Bdbw(1px) Bdbs(s) Bdc($c-fuji-grey-c) H(36px) "><td class="C(black) W(51%)"><span>Open</span></td><td class="Ta(end) Fw(b) Lh(14px)" data-test="OPEN-value"><span class="Trsdu(0.3s) ">216.60</span></td></tr>
    print("summary_table=%s" % summary_table)
    summary_data = OrderedDict()
    other_details_json_link = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?formatted=true&lang=en-US&region=US&modules=summaryProfile%2CfinancialData%2CrecommendationTrend%2CupgradeDowngradeHistory%2Cearnings%2CdefaultKeyStatistics%2CcalendarEvents&corsDomain=finance.yahoo.com".format(
        ticker)
    summary_json_response = requests.get(other_details_json_link)
    try:
        json_loaded_summary = json.loads(summary_json_response.text)
        y_Target_Est = json_loaded_summary["quoteSummary"]["result"][0]["financialData"]["targetMeanPrice"]['raw']
        earnings_list = json_loaded_summary["quoteSummary"]["result"][0]["calendarEvents"]['earnings']
        eps = json_loaded_summary["quoteSummary"]["result"][0]["defaultKeyStatistics"]["trailingEps"]['raw']
        datelist = []
        for i in earnings_list['earningsDate']:
            datelist.append(i['fmt'])
        earnings_date = ' to '.join(datelist)
        for table_data in summary_table:
            raw_table_key = table_data.xpath('.//td[contains(@class,"C(black)")]//text()')
            raw_table_value = table_data.xpath('.//td[contains(@class,"Ta(end)")]//text()')
            table_key = ''.join(raw_table_key).strip()
            table_value = ''.join(raw_table_value).strip()
            summary_data.update({table_key: table_value})
        summary_data.update(
            {'1y Target Est': y_Target_Est, 'EPS (TTM)': eps, 'Earnings Date': earnings_date, 'ticker': ticker,
             'url': url})
        return summary_data
    except:
        print("Failed to parse json response")
        return {"error": "Failed to parse json response"}


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('ticker', help='')
    args = argparser.parse_args()
    ticker = args.ticker
    print("Fetching data for %s" % (ticker))
    scraped_data = parse(ticker)
    print("Writing data to output file")
    with open('%s-summary.json' % (ticker), 'w') as fp:
        json.dump(scraped_data, fp, indent=4)

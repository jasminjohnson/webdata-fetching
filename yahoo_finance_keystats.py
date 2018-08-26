from lxml import html
import requests
from time import sleep
import json
import argparse
from collections import OrderedDict
from time import sleep

from lxml import etree, html


def parse(ticker):
    # url = "http://finance.yahoo.com/quote/%s?p=%s" % (ticker, ticker)
    # url = "https://finance.yahoo.com/quote/%s?p=%s" % (ticker, ticker)
    url = "https://finance.yahoo.com/quote/%s/key-statistics?p=%s" % (ticker, ticker)
    # response = requests.get(url, verify=False)
    response = requests.get(url)
    print("Parsing %s" % (url))
    sleep(10)
    parser = html.fromstring(response.text)

    # print("response=%s" % response.content)
    # print("==== summary_table ====")
    # print(etree.tostring(parser, encoding='unicode', pretty_print=True))

    ## //*[@id="Col1-0-KeyStatistics-Proxy"]/section/div/div/div/div/table/tbody/tr
    ## //*[@id="Col1-3-KeyStatistics-Proxy"]/section/div/div/div/div/div/table/tbody/tr
    try:
        summary_table = parser.xpath('//*[@id="Col1-3-KeyStatistics-Proxy"]/section/div/div/div/div//*/tr')
        print("summary_table=%s" % summary_table)
        summary_data = OrderedDict()
        for table_data in summary_table:
            # raw_table_key = table_data.xpath('.//td[contains(@class,"C(black)")]//text()')
            # raw_table_value = table_data.xpath('.//td[contains(@class,"Ta(end)")]//text()')
            ## //*[@id="Col1-0-KeyStatistics-Proxy"]/section/div[2]/div[1]/div[1]/div/table/tbody/tr[1]/td[1]/span
            raw_table_key = table_data.xpath('.//td[1]/span//text()')
            raw_table_value = table_data.xpath('.//td[2]//text()')
            table_key = ''.join(raw_table_key).strip()
            table_value = ''.join(raw_table_value).strip()
            summary_data.update({table_key: table_value})
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
    with open('%s-keystats.json' % (ticker), 'w') as fp:
        json.dump(scraped_data, fp, indent=4)

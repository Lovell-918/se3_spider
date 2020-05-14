# coding=utf-8
import csv
import json
import re

import requests
from lxml import html

from bs4 import BeautifulSoup
import random
import urllib3

ip_random = -1
article_tag_list = []
article_type_list = []
csv_links = list()
etree = html.etree

# ase
# https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=ASE&highlight=true&returnType=SEARCH&returnFacets=ALL&refinements=PublicationTitle:2019%2034th%20IEEE%2FACM%20International%20Conference%20on%20Automated%20Software%20Engineering%20(ASE)&refinements=PublicationTitle:2017%2032nd%20IEEE%2FACM%20International%20Conference%20on%20Automated%20Software%20Engineering%20(ASE)&refinements=PublicationTitle:2015%2030th%20IEEE%2FACM%20International%20Conference%20on%20Automated%20Software%20Engineering%20(ASE)&refinements=PublicationTitle:2016%2031st%20IEEE%2FACM%20International%20Conference%20on%20Automated%20Software%20Engineering%20(ASE)&refinements=PublicationTitle:2013%2028th%20IEEE%2FACM%20International%20Conference%20on%20Automated%20Software%20Engineering%20(ASE)

# icse
# https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=ICSE&highlight=true&returnType=SEARCH&refinements=PublicationTitle:2015%20IEEE%2FACM%2037th%20IEEE%20International%20Conference%20on%20Software%20Engineering&refinements=PublicationTitle:2018%20IEEE%2FACM%2040th%20International%20Conference%20on%20Software%20Engineering%20(ICSE)&refinements=PublicationTitle:2019%20IEEE%2FACM%2041st%20International%20Conference%20on%20Software%20Engineering%20(ICSE)&refinements=PublicationTitle:2016%20IEEE%2FACM%2038th%20International%20Conference%20on%20Software%20Engineering%20(ICSE)&refinements=PublicationTitle:2017%20IEEE%2FACM%2039th%20International%20Conference%20on%20Software%20Engineering%20(ICSE)&returnFacets=ALL

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 ' \
             'Safari/537.36 '

# TODO 修改这里为自己想要存储爬取数据导出的根路径，建议不要出现中文
base_path = "C:\\Users\\laiba\\Documents\\temp\\"

urllib3.disable_warnings()


def get_keywords(keywords):
    for kds in keywords:
        if kds["type"] == 'IEEE Keywords':
            return kds["kwd"]
    return []


def get_proxie(random_number):
    with open('ip.txt', 'r') as file:
        ip_list = json.load(file)
        if random_number == -1:
            random_number = random.randint(0, len(ip_list) - 1)
        ip_info = ip_list[random_number]
        ip_url_next = '://' + ip_info['address'] + ':' + ip_info['port']
        proxies = {'http': 'http' + ip_url_next, 'https': 'https' + ip_url_next}
        return random_number, proxies


def ieee_all_info(url):
    global ip_random
    headers = {'User-Agent': USER_AGENT}

    ip_rand, proxies = get_proxie(ip_random)
    try:
        res = requests.get(url=url, headers=headers, proxies=proxies, timeout=3)
    except:
        request_status = 500
    else:
        request_status = res.status_code
    while request_status != 200:
        ip_random = -1
        ip_rand, proxies = get_proxie(ip_random)
        try:
            res = requests.get(url=url, headers=headers, proxies=proxies, timeout=3)
        except:
            request_status = 500
        else:
            request_status = res.status_code
    ip_random = ip_rand

    if res is not None:
        pattern = re.compile(ur'metadata={.*};')
        re_con = pattern.search(res.text)
        if re_con is None:
            content = ""
        else:
            content = json.loads(re_con.group()[9:-1])
    else:
        content = ""
    if 'title' in content:
        document_title = content['title']
    else:
        document_title = ''

    if 'authors' in content:
        authors_temp = content['authors']
        authors = list()
        for at in authors_temp:
            au = at['name']
            af = at['affiliation']
            ja_aa = dict(
                author=au,
                affiliation=af
            )
            authors.append(ja_aa)
    else:
        authors = list()

    if 'publicationTitle' in content:
        publication_title = content['publicationTitle']
    else:
        publication_title = ''
    date_added_to_xplore = ''

    if 'publicationYear' in content:
        publication_year = content['publicationYear']
    else:
        publication_year = ''
    volume = ''
    issue = ''
    if 'startPage' in content:
        start_page = content['startPage']
    else:
        start_page = ''
    if 'endPage' in content:
        end_page = content['endPage']
    else:
        end_page = ''

    if 'abstract' in content:
        abstract = content['abstract']
    else:
        abstract = ''
    issn = ""
    isbns = ""

    if 'doi' in content:
        doi = content['doi']
    else:
        doi = ''
    funding_information = ''
    if 'pdfUrl' in content:
        pdf_link = content['pdfUrl']
    else:
        pdf_link = ''

    author_keywords = list()
    ieee_terms = list()
    inspec_controlled_terms = list()
    inspec_non_controlled_terms = list()
    mesh_terms = list()
    bing_terms = list()
    if 'keywords' in content:
        keywords = content['keywords']
        for kds in keywords:
            if 'type' not in kds.keys():
                mesh_terms = kds['kwd']
            elif kds['type'] == 'IEEE Keywords':
                ieee_terms = kds["kwd"]
            elif kds['type'] == 'INSPEC: Controlled Indexing':
                inspec_controlled_terms = kds['kwd']
            elif kds['type'] == 'INSPEC: Non-Controlled Indexing':
                inspec_non_controlled_terms = kds['kwd']
            elif kds['type'] == 'Author Keywords ':
                author_keywords = kds['kwd']
    if 'citationCount' in content:
        article_citation_count = content['citationCount']
    else:
        article_citation_count = ''
    reference_count = ''
    licence = ''
    if 'onlineDate' in content:
        online_date = content['onlineDate']
    else:
        online_date = ''
    issue_date = ''
    if 'conferenceDate' in content:
        meeting_date = content['conferenceDate']
    else:
        meeting_date = ''
    if 'publisher' in content:
        publisher = content['publisher']
    else:
        publisher = ''
    document_identifier = ''

    paper = dict(
        document_title=document_title, authors=authors, publication_title=publication_title,
        date_added_to_xplore=date_added_to_xplore, publication_year=publication_year, volume=volume,
        issue=issue, start_page=start_page, end_page=end_page, abstract=abstract, issn=issn, isbns=isbns,
        doi=doi, funding_information=funding_information, pdf_link=pdf_link, authors_keywords=author_keywords,
        ieee_terms=ieee_terms, inspec_controlled_terms=inspec_controlled_terms,
        inspec_non_controlled_terms=inspec_non_controlled_terms, mesh_terms=mesh_terms, bing_terms=bing_terms,
        article_citation_count=article_citation_count, reference_count=reference_count, licence=licence,
        online_date=online_date, issue_date=issue_date, meeting_date=meeting_date, publisher=publisher,
        document_identifier=document_identifier
    )
    return paper


def trans_paper_row(paper):
    row = [paper['document_title']]
    aas = paper['authors']
    author_list = list()
    affi_list = list()
    for aa in aas:
        author_list.append(aa['author'])
        affi_list.append(aa['affiliation'])
    author = ','.join(author_list)
    affi = ','.join(affi_list)
    row.append(author)
    row.append(affi)
    row.append(paper['publication_title'])
    row.append(paper['date_added_to_xplore'])
    row.append(paper['publication_year'])
    row.append(paper['volume'])
    row.append(paper['issue'])
    row.append(paper['start_page'])
    row.append(paper['end_page'])
    row.append(paper['abstract'])
    row.append(paper['issn'])
    row.append(paper['isbns'])
    row.append(paper['doi'])
    row.append(paper['funding_information'])
    row.append(paper['pdf_link'])
    row.append(','.join(paper['authors_keywords']))
    row.append(','.join(paper['ieee_terms']))
    row.append(','.join(paper['inspec_controlled_terms']))
    row.append(','.join(paper['inspec_non_controlled_terms']))
    row.append(','.join(paper['mesh_terms']))
    row.append(','.join(paper['bing_terms']))
    row.append(paper['article_citation_count'])
    row.append(paper['reference_count'])
    row.append(paper['licence'])
    row.append(paper['online_date'])
    row.append(paper['issue_date'])
    row.append(paper['meeting_date'])
    row.append(paper['publisher'])
    row.append(paper['document_identifier'])
    return row


def filter_refrence(refence, csv_write):
    global csv_links
    # global ip_random

    nRe = json.dumps(refence)
    arrayRef = json.loads(nRe)
    my_res = []

    for i in arrayRef:
        t_i = json.dumps(i)
        con = json.loads(t_i)

        if 'title' in con:
            title = con['title']
        else:
            title = ''
        if 'links' in con:
            t_con = json.dumps(con['links'])
            link_con = json.loads(t_con)
            if 'documentLink' in link_con:
                link = link_con['documentLink']
            else:
                link = ''
            if 'crossRefLink' in link_con:
                doi = link_con['crossRefLink'].replace('https://doi.org/', '')
            else:
                doi = ''
        else:
            link = ''
            doi = ''
        # 存储引文详情
        if link != '':
            url = "https://ieeexplore.ieee.org" + link
            if link not in csv_links:
                paper = ieee_all_info(url)
                if doi == '':
                    doi = paper['doi']
                row = trans_paper_row(paper)
                csv_write.writerow([text.encode("utf8") for text in row])
            else:
                if doi == '':
                    paper = ieee_all_info(url)
                    doi = paper['doi']
        else:
            # https://cn.bing.com/academic/?q
            if 'googleScholarLink' in con:
                origin_google_link = con['googleScholarLink']
                beg = origin_google_link.find('as_q=') + 5
                end = origin_google_link.find('&')
                scholar_link = con['googleScholarLink'][beg:end]
            else:
                scholar_link = title.replace(" ", "+")
            headers = {'User-Agent': USER_AGENT}
            # url = 'https://cn.bing.com/academic/?q=' + scholar_link
            # params = {"mkt": "zh-CN", 'first': 1}
            # ip_rand, proxies = get_proxie(ip_random)
            # try:
            #     res = requests.get(url=url, params=params, headers=headers, proxies=proxies, timeout=3)
            # except:
            #     request_status = 500
            # else:
            #     request_status = res.status_code
            # while request_status != 200:
            #     ip_random = -1
            #     ip_rand, proxies = get_proxie(ip_random)
            #     try:
            #         res = requests.get(url=url, params=params, headers=headers, proxies=proxies, timeout=3)
            #     except:
            #         request_status = 500
            #     else:
            #         request_status = res.status_code
            # ip_random = ip_rand
            url = 'https://cn.bing.com/academic/?q=' + scholar_link
            params = {"mkt": "zh-CN", 'first': 1}
            res = requests.get(url=url, params=params, headers=headers, verify=False)
            if res is not None:
                ehtml = etree.HTML(res.text)
                result = ehtml.xpath('//*[@id="b_results"]/li[%s]/h2/a/@href' % 1)
                if result and result[0].startswith('/academic/profile?id='):
                    paper_url = 'https://cn.bing.com' + result[0]

                    # ip_rand, proxies = get_proxie(ip_random)
                    # try:
                    #     paper_res = requests.get(url=paper_url, headers=headers, proxies=proxies, timeout=3)
                    # except:
                    #     request_status = 500
                    # else:
                    #     request_status = paper_res.status_code
                    # while request_status != 200:
                    #     ip_random = -1
                    #     ip_rand, proxies = get_proxie(ip_random)
                    #     try:
                    #         paper_res = requests.get(url=paper_url, headers=headers, proxies=proxies, timeout=3)
                    #     except:
                    #         request_status = 500
                    #     else:
                    #         request_status = paper_res.status_code
                    # ip_random = ip_rand

                    paper_res = requests.get(url=paper_url, headers=headers, verify=False)

                    paper_ehtml = etree.HTML(paper_res.text)
                    trs = paper_ehtml.xpath('//*[@class="aca_base"]/li[@class="aca_title"]')
                    document_title = trs[0].text
                    authors = list()
                    abstract = ''
                    bing_terms = list()
                    publication_year = ''
                    start_page = ''
                    end_page = ''
                    article_citation_count = ''
                    publisher = ''
                    for i in range(1, 12):
                        labels = paper_ehtml.xpath(
                            '//*[@class="aca_main"]/ul[@class="b_vList b_divsec"]/li[' + str(i) + ']/div[ '
                                                                                                  '@class="b_hPanel"]/span[@class="aca_labels"]/span/text()')
                        if labels:
                            label = labels[0].encode('utf-8')
                        else:
                            break
                        if label == '作　　者':
                            trs = paper_ehtml.xpath(
                                '//*[@class="aca_main"]/ul[@class="b_vList b_divsec"]/li[' + str(i) + ']/div['
                                                                                                      '@class="b_hPanel"]/span[@class="aca_content"]/div[@class="aca_desc '
                                                                                                      'b_snippet"]/span/a')
                            for at in trs:
                                au = at.text
                                ja_aa = dict(
                                    author=au,
                                    affiliation='NA'
                                )
                                authors.append(ja_aa)
                        elif label == '摘　　要':
                            trs = paper_ehtml.xpath(
                                '//*[@class="aca_main"]/ul[@class="b_vList b_divsec"]/li[' + str(i) + ']/div['
                                                                                                      '@class="b_hPanel"]/span[@class="aca_content"]/div[@class="aca_desc '
                                                                                                      'b_snippet"]/span/span/@title')
                            if trs:
                                abstract = trs[0]
                        elif label == '研究领域':
                            bing_terms = paper_ehtml.xpath(
                                '//*[@class="aca_main"]/ul[@class="b_vList b_divsec"]/li[' + str(i) + ']/div['
                                                                                                      '@class="b_hPanel"]/span[@class="aca_content"]/div/span/ '
                                                                                                      'a/text()')
                        elif label == '发表日期':
                            trs = paper_ehtml.xpath(
                                '//*[@class="aca_main"]/ul[@class="b_vList b_divsec"]/li[' + str(i) + ']/div[ '
                                                                                                      '@class="b_hPanel"]/span[@class="aca_content"]/div/text()')
                            if trs:
                                publication_year = trs[0]
                        elif label == '会 　议' or label == '期　　刊':
                            trs = paper_ehtml.xpath(
                                '//*[@class="aca_main"]/ul[@class="b_vList b_divsec"]/li[' + str(i) + ']/div[ '
                                                                                                      '@class="b_hPanel"]/span[@class="aca_content"]/div/a/text()')
                            if trs:
                                publisher = trs[0]
                        elif label == '页码范围':
                            trs = paper_ehtml.xpath(
                                '//*[@class="aca_main"]/ul[@class="b_vList b_divsec"]/li[' + str(i) + ']/div[ '
                                                                                                      '@class="b_hPanel"]/span[@class="aca_content"]/div/text()')
                            if trs:
                                pages = trs[0].split('-')
                                start_page = pages[0]
                                if len(pages) == 1:
                                    end_page = start_page
                                else:
                                    end_page = pages[1]
                        elif label == '被 引 量':
                            trs = paper_ehtml.xpath(
                                '//*[@class="aca_main"]/ul[@class="b_vList b_divsec"]/li[' + str(i) + ']/div[ '
                                                                                                      '@class="b_hPanel"]/span[@class="aca_content"]/div/text()')
                            if trs:
                                article_citation_count = trs[0]
                        elif label == 'DOI':
                            trs = paper_ehtml.xpath(
                                '//*[@class="aca_main"]/ul[@class="b_vList b_divsec"]/li[' + str(i) + ']/div[ '
                                                                                                      '@class="b_hPanel"]/span[@class="aca_content"]/div/text()')
                            if trs:
                                doi = trs[0]
                else:
                    continue
                paper = dict(
                    document_title=document_title, authors=authors, publication_title='',
                    date_added_to_xplore='', publication_year=publication_year, volume='',
                    issue='', start_page=start_page, end_page=end_page, abstract=abstract, issn='', isbns='',
                    doi=doi, funding_information='', pdf_link='',
                    authors_keywords=list(), ieee_terms=list(), inspec_controlled_terms=list(),
                    inspec_non_controlled_terms=list(), mesh_terms=list(), bing_terms=bing_terms,
                    article_citation_count=article_citation_count, reference_count='', licence='',
                    online_date='', issue_date='', meeting_date='', publisher=publisher,
                    document_identifier=''
                )
                csv_write.writerow([text.encode("utf8") for text in trans_paper_row(paper)])
            else:
                continue
        sin = dict(
            title=title,
            link=link,
            doi=doi
        )
        my_res.append(sin)
    return my_res


def get_reference(url, link_num, csv_write):
    headers = {"Connection": "close", "Accept": "application/json, text/plain, */*", "cache-http-response": "true",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3377.1 Safari/537.36",
               "Referer": "https://ieeexplore.ieee.org/document/" + link_num + "/references",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}

    global ip_random

    ip_rand, proxies = get_proxie(ip_random)
    try:
        res = requests.get(url=url, headers=headers, proxies=proxies, timeout=3)
    except:
        request_status = 500
    else:
        request_status = res.status_code
    while request_status != 200:
        ip_random = -1
        ip_rand, proxies = get_proxie(ip_random)
        try:
            res = requests.get(url=url, headers=headers, proxies=proxies, timeout=3)
        except:
            request_status = 500
        else:
            request_status = res.status_code
    ip_random = ip_rand

    if res is not None:
        content = json.loads(res.text)
    else:
        content = ""
    if 'references' in content:
        reference = filter_refrence(content["references"], csv_write)
    else:
        reference = list()
    return reference


def ieee_info(url):
    global ip_random
    headers = {'User-Agent': USER_AGENT}

    ip_rand, proxies = get_proxie(ip_random)
    try:
        res = requests.get(url=url, headers=headers, proxies=proxies, timeout=3)
    except:
        request_status = 500
    else:
        request_status = res.status_code
    while request_status != 200:
        ip_random = -1
        ip_rand, proxies = get_proxie(ip_random)
        try:
            res = requests.get(url=url, headers=headers, proxies=proxies, timeout=3)
        except:
            request_status = 500
        else:
            request_status = res.status_code
    ip_random = ip_rand

    if res is not None:
        pattern = re.compile(ur'metadata={.*};')
        re_con = pattern.search(res.text)
        if re_con is None:
            content = ""
        else:
            content = json.loads(re_con.group()[9:-1])
    else:
        content = ""
    # if 'title' in content:
    #     title = content['title']
    # else:
    #     title = ''

    if 'authors' in content:
        authors = content['authors']
    else:
        authors = list()

    # if 'abstract' in content:
    #     abstract = content['abstract']
    # else:
    #     abstract = ''
    #
    # if 'publicationTitle' in content:
    #     publication = content['publicationTitle']
    # else:
    #     publication = ''
    #
    # if 'keywords' in content:
    #     keywords = get_keywords(content['keywords'])
    # else:
    #     keywords = list()
    #
    # if 'doi' in content:
    #     doi = content['doi']
    # else:
    #     doi = ''

    paper = dict(
        # title=title,
        authors=authors
        # abstract=abstract,
        # publication=publication,
        # keywords=keywords
        # doi=doi
    )
    return paper


def ieee_parse(csv_path):
    # ase
    # ase_res = open(base_path + 'ase_res.json', 'a')
    # icse
    # icse_complete_res = open(base_path + 'icse_complete_ref.json', 'a')
    icse_res = open(base_path + 'icse_ref.json', 'a')
    my_f = open(base_path + 'icse_complete_ref.csv', 'ab')
    csv_write = csv.writer(my_f)

    res = []

    csv_row = ['Document Title', 'Authors', 'Author Affiliations', 'Publication Title', 'Date Added To Xplore',
               'Publication Year', 'Volume', 'Issue', 'Start Page', 'End Page', 'Abstract', 'ISSN', 'ISBNs', 'DOI',
               'Funding Information', 'PDF Link', 'Author Keywords', 'IEEE Terms', 'INSPEC Controlled Terms',
               'INSPEC Non-Controlled Terms', 'Mesh_Terms', 'Bing Terms', 'Article Citation Count', 'Reference Count',
               'License', 'Online Date', 'Issue Date', 'Meeting Date', 'Publisher', 'Document Identifier']
    csv_write.writerow(csv_row)
    with open(csv_path) as f:
        rows = csv.reader(f)
        headers = next(rows)
        for row in rows:
            publish_title = row[3]
            pdf_link = str(row[15])
            link_num = pdf_link[pdf_link.rfind('=') + 1:]

            # if str(link_num) == '8952245':
            #     flag = True

            # if flag is False:
            #     continue

            url = "https://ieeexplore.ieee.org/document/" + link_num

            print url
            paper = ieee_info(url)
            ref_url = "https://ieeexplore.ieee.org/rest/document/" + link_num + "/references"

            if len(paper['authors']) != 0:
                single = dict()
                single['pdf_link'] = u''.join(pdf_link).encode('utf-8').strip()
                # single['authors'] = paper['authors']
                # single['abstract'] = u''.join(paper['abstract']).encode('utf-8').strip()
                # single['keywords'] = u''.join(paper['keywords']).encode('utf-8').strip()
                # single['publication'] = u''.join(paper['publication']).encode('utf-8').strip()
                # single['doi'] = u''.join(paper['doi']).encode('utf-8').strip()
                ref = get_reference(ref_url, link_num, csv_write)
                single['ref'] = ref

                res.append(json.dumps(single))

                # ase_res.write(json.dumps(single) + '\n')
                # ase_res.flush()
                # ase_res.close()
                icse_res.write(json.dumps(single) + '\n')
                icse_res.flush()
    icse_res.close()
    my_f.close()


def format_reference(ref):
    res = list()
    for s in ref:
        if len(s.strip()) == 0:
            pass
        else:
            res.append(s)
    return res


def get_all_link_in_csv(csv_path):
    global csv_links
    with open(csv_path) as f:
        rows = csv.reader(f)
        for row in rows:
            pdf_link = str(row[15])
            link_num = pdf_link[pdf_link.rfind('=') + 1:]
            csv_links.append("/document/" + link_num)


if __name__ == '__main__':
    # TODO 修改这里为自己存储数据源的文件位置，建议路径里不要出现中文
    get_all_link_in_csv("C:\\Users\\laiba\\Documents\\temp\\icse15_16_17_18_19.csv")
    get_all_link_in_csv("C:\\Users\\laiba\\Documents\\temp\\ase13_15_16_17_19.csv")
    ieee_parse("C:\\Users\\laiba\\Documents\\temp\\icse15_16_17_18_19.csv")

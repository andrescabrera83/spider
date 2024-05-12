from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory, jsonify
import os
from os import environ
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider
from scrapy.http import Request
from pathlib import Path
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

import datetime
from datetime import datetime

import socket

app = Flask(__name__)

def find_available_port(start_port=1024, end_port=65535):
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError as e:
                continue
    return None

# Define Scrapy spider to download PDF and extract text
class PDFSpiderJMG(Spider):
    name = 'pdf_spider'
    start_urls = ['https://www.jornalminasgerais.mg.gov.br']

    def __init__(self):
        self.cursor: None
        chrome_options = Options()
        
        # Set download directory and disable prompt for file downloads
        prefs = {
            'download.default_directory': '/home/rdpuser/diariospdf/pdf_highlighter/static',
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': False
        } 
        chrome_options.add_experimental_option('prefs', prefs)
        #chrome_options.add_argument(f"--download.default_directory={prefs}")
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def start_requests(self):
        url = self.start_urls[0]
        self.driver.get(url)
        time.sleep(3)
        self.driver.find_element(By.ID, "linkDownloadPDF").click()
        time.sleep(4)
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        pdf_url = response.xpath('//*[@id="linkDownloadPDF"]/@href').get()
        if pdf_url:
             yield Request(pdf_url, callback=self.save_pdf)
        else:
            self.logger.error('PDF URL not found on the webpage')


    def save_pdf(self, response):
        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition:
            
            file_name = content_disposition.split('filename=')[-1].strip('"')
            file_path = os.path.join('/home/rdpuser/diariospdf/pdf_highlighter/static', file_name)
            print("File path found:", file_path)
            with open(file_path, 'wb') as f:
                f.write(response.body)
            
        else:
            print("Content-Disposition header not found. Unable to determine file name.")


# Define Scrapy spider to download PDF and extract text
class PDFSpiderDOU(scrapy.Spider):
    name = 'pdf_spider'
    start_urls = ['https://www.in.gov.br/leiturajornal']

    def __init__(self):
        self.cursor: None
        chrome_options = webdriver.ChromeOptions()
        
        # Set download directory and disable prompt for file downloads
        prefs = {
            'download.default_directory': '/home/rdpuser/diariospdf/pdf_highlighter/static',
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': False
        } 
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_argument("--headless")
        
        self.driver = webdriver.Chrome(options=chrome_options)

    def start_requests(self):
        # Step 1: Navigate to https://www.in.gov.br/leiturajornal
        self.driver.get(self.start_urls[0])
        time.sleep(3)
        
        # Step 2: Click on the "DIÁRIO COMPLETO" button
        self.driver.find_element(By.CLASS_NAME, "btn-diario-completo").click()
        time.sleep(4)
        
        self.driver.find_element(By.CSS_SELECTOR, "a[title='Download da edição completa.']").click()
        



# Function to start the Scrapy spider for JMG
def run_spiderJMG():
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    })
    process.crawl(PDFSpiderJMG)
    process.start()

# Function to start the Scrapy spider for DOU
def run_spiderDOU():
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    })
    process.crawl(PDFSpiderDOU)
    process.start()


if __name__ == "__main__":

    ## FIRST JORNAL MINAS GERAIS ######################################

    #get today's date
    todayJMG = datetime.today().strftime('%Y-%m-%d')

    #construct the filename
    filename_patternJMG = f'caderno1_{todayJMG}.pdf'

    #filer PDF files based on the filename pattern
    today_fileJMG = [f for f in os.listdir('/home/rdpuser/diariospdf/pdf_highlighter/static')  if f.startswith('caderno1') and f.endswith(f'_{todayJMG}.pdf')]

    if not today_fileJMG:
        print("No file found for today's JMG date, procced to download JMG")
        run_spiderJMG()

    else:
        print("JMG file already saved")

    #SECOND DIARIO OFICIAL DA UNIAO DOU #######################################

    #get today's date
    todayDOU = datetime.today().strftime('%Y_%m_%d')

    #construct the filename
    filename_patternDOU = f'{todayDOU}_ASSINADO_do1.pdf'

    #filer PDF files based on the filename pattern
    today_fileDOU = [f for f in os.listdir('/home/rdpuser/diariospdf/pdf_highlighter/static') if f.startswith(todayDOU) and f.endswith('.pdf')]

    if not today_fileDOU:
        print("No file found for today's date, procced to download")
        run_spiderDOU()

    else:
        print("file already saved")


    ## Find an available port dynamically
    #available_port = find_available_port()
    #if available_port:
    #    print(f"Found available port: {available_port}")
    #    app.run(host='0.0.0.0', port=available_port)
    #else:
    #    print("No available ports found. Exiting.")

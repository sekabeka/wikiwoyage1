from playwright.async_api import async_playwright, Page
from fake_useragent import UserAgent
from bs4 import BeautifulSoup, Tag
import lxml
import re
import time
import json
import requests
import pandas as pd
import asyncio
import random


errors = []

async def main():
	async with async_playwright() as p:
		browser =  await p.firefox.launch(headless=True)
		context = await browser.new_context()
		page = await context.new_page() 
		p = pd.read_csv('world-cities.csv').to_dict('list')
		citys = p['name']
		countries = p['country']
		links = ['https://en.wikivoyage.org/wiki/' + i for  i in citys]
		tasks = []
		result = []
		for url, city, country, in zip(links, citys, countries[:20]):
			pages = [await context.new_page() for _ in range (1, random.randint(4, 12))]
			while pages:
				page = pages.pop()
				if 'city' in url.lower():
					url = re.sub(r'city', '', url, flags=re.IGNORECASE)
				url = url.replace(' ', '_')
				task = asyncio.create_task(data(url, page, country, city))
				tasks.append(task)
			result += await asyncio.gather(*tasks)
			tasks.clear()
		len_errors = 0
		while len_errors != len(errors):
			len_errors = len(errors)
			print (f'Ошибок {len(errors)}')
			while errors:
				url, country, city = errors.pop()
				result.append(await data(url, page, country, city))
			print (f'Ошибок после попытки их исправить {len(errors)}')

		with open('asdasdasd.json', 'w', encoding='utf-8') as js:
			json.dump(result, js, ensure_ascii=False, indent=4)






async def data(url:str, page:Page, country:str, city:str):
	try:
		await page.goto(url)
		await asyncio.sleep(3)
	except:
		errors.append(
			(url, country, city)
		)
		print ('ошибочка')
		return []
	print ('+')
	soup = BeautifulSoup(await page.inner_html('body'), 'lxml')
	main_div = soup.find('div', id='bodyContent').find('div', id='mw-content-text')
	main_text = ''
	sections = main_div.find_all('div', class_='mw-h2section')
	for p in main_div.div.find_all('p', recursive=False):
		main_text += p.text
	
	result = {
	'city' : city,
	'country' : country,
	'main text' : main_text,
	'url' : url
	}
	tmp = []
	for section in sections:
		if section.table:
			section.table.decompose()
		if section.ul:
			section.ul.decompose()
		if section.figure:
			section.figure.decompose()
		if section.img:
			section.img.decompose()
		
		name = section.h2.span.text.strip()
		result_text = ''
		for paragraph in section.find_all('p'):
			try:
				result_text += paragraph.text.strip()
			except Exception as e:
				print (e)
		tmp.append(
			{
				name : result_text
			}
		)
	result['some points'] = tmp
	return result
	
	


asyncio.run(main())



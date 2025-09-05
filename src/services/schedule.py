import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any
import textwrap
import logging 

logger = logging.getLogger(__name__)

class ScheduleParserService:
    
    group_name: str
    url_parse_group: str = "https://portal.esstu.ru/bakalavriat/raspisan.htm"

    def __init__(self, group_name: str) -> None:
        logger.debug("Schedule parser initialized")
        self.group_name = group_name

    def find_group_schedule_url(self, group_number: str):
        logger.debug("Method find_grou[_schedule_url is called")
        try:

            logger.debug(f"Sending request to {self.url_parse_group}")
            response = requests.get(self.url_parse_group)
            response.encoding = 'windows-1251'  
            logger.debug(f"Response object: {response}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True)
                if group_number.lower() in link_text.lower():
                    if isinstance(link, Tag):
                        return str(link.get("href"))
                    else: 
                        logger.warning("Link has not a Tag type")
                        return None
            return None
        except Exception as e:
            print(f"Ошибка при обработке: {e}")
            return None

    def url_schedule(self, group_name: str) -> str:
        return f"https://portal.esstu.ru/bakalavriat/{group_name}"


    def parse_schedule(self) -> List[Dict[str, Any]] | None:
        group = self.find_group_schedule_url(self.group_name)

        if not group:
            logger.warning("Group has not found")
            return None
        
        url = self.url_schedule(group)

        logger.debug(f"Send request to {url}")
        response = requests.get(url)
        response.encoding = "windows-1251"
        logger.debug(f"Response object: {response}")

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        time_row = soup.find_all('tr')[1]

        if not isinstance(time_row, Tag):
            logger.warning("Object time_row has not Tag type")
            return None 
        
        times = [td.get_text(strip=True) for td in time_row.find_all('td')[1:7]]
        today = datetime.now(tz=timezone(timedelta(hours=8)))

        day = today.day
        index = day - 15
        week = 1 if index / 2 <= 7 else 2

        days_map = {
            'Пнд': 'Понедельник',
            'Втр': 'Вторник', 
            'Срд': 'Среда',
            'Чтв': 'Четверг',
            'Птн': 'Пятница',
            'Сбт': 'Суббота'
        }

        week1 = []

        for row in soup.find_all('tr')[2:]:

            if not isinstance(row, Tag):
                logger.warning(f"Object row has not type Tag")
                return None 
            
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
                
            day_cell = cells[0]

            if not isinstance(day_cell, Tag):
                logger.warning("Object day cell has not type Tag")
                return None
            
            day_text = day_cell.get_text(strip=True)
            
            is_week2 = day_cell.find('font', color="#0000ff") is not None
            day_name = days_map.get(day_text, day_text)
            
            for i, cell in enumerate(cells[1:7]):

                subject = cell.get_text(' ', strip=True)
                if subject == '_' or not subject:
                    continue
                    
                pair_info = {
                    'day': day_name,
                    'time': times[i],
                    'subject': subject,
                    'week': 2 if is_week2 else 1
                }
                if week != pair_info['week']:
                    continue
                
                week1.append(pair_info)
        
        logger.debug(f"Week 1: {week1}")
        return week1

    def get_week_number(self, date: datetime):
        start_date = datetime(2023, 9, 1) 
        delta = date - start_date
        week_num = (delta.days // 7) % 2 + 1
        return week_num

    def create_schedule_image(
        self, 
        day_schedule: List[Dict[str, str]], 
        date: datetime, 
        title: str
    ):
        width, height = 1000, 600
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        try:
            title_font = ImageFont.truetype("arialmt.ttf", 24)
            font = ImageFont.truetype("arialmt.ttf", 18)
            small_font = ImageFont.truetype("arialmt.ttf", 14)

        except:
            title_font = ImageFont.load_default()
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        draw.text((20, 20), f"{title} ({date.strftime('%d.%m.%Y')})", fill='black', font=title_font)
        
        draw.line([(20, 60), (width - 20, 60)], fill='black', width=2)
        
        y_position = 80
        time_width = 150
        subject_width = width - time_width - 60
        
        if not day_schedule:
            draw.text((20, y_position), "Пар нет", fill='black', font=font)
            return image
        
        draw.text((20, y_position), "Время", fill='black', font=font)
        draw.text((20 + time_width, y_position), "Предмет и аудитория", fill='black', font=font)
        
        y_position += 30
        draw.line([(20, y_position), (width - 20, y_position)], fill='black', width=1)
        y_position += 10
        
        for i, pair in enumerate(day_schedule, start=1):
            draw.text((20, y_position), pair['time'], fill='black', font=font)
            
            subject_text = pair['subject']
            wrapped_text = textwrap.fill(subject_text, width=50)
            lines = wrapped_text.split('\n')
            
            for line in lines:
                if y_position > height - 50:
                    draw.text((20 + time_width, y_position), "...", fill='black', font=font)
                    return image
                draw.text((20 + time_width, y_position), line, fill='black', font=small_font)
                y_position += 20
            
            y_position += 10
            draw.line([(20, y_position), (width - 20, y_position)], fill='gray', width=1)
            y_position += 20
            
            if y_position > height - 50:
                break
        
        return image

    def get_today_tomorrow_schedule(self):
        week1 = self.parse_schedule()

        if not week1:
            logger.warning("Object week has not found")
            return None
        
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        current_week = self.get_week_number(today)
        tomorrow_week = self.get_week_number(tomorrow)
        
        days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
        today_name = days[today.weekday()]
        tomorrow_name = days[tomorrow.weekday()]
        
        if current_week == 1:
            today_schedule = [p for p in week1 if p['day'] == today_name]
        else:
            today_schedule = [p for p in week1 if p['day'] == today_name]
        
        if tomorrow_week == 1:
            tomorrow_schedule = [p for p in week1 if p['day'] == tomorrow_name]
        else:
            tomorrow_schedule = [p for p in week1 if p['day'] == tomorrow_name]
        
        def time_key(pair):
            return pair['time']
        
        today_schedule.sort(key=time_key)
        tomorrow_schedule.sort(key=time_key)
        
        return today_schedule, tomorrow_schedule, today, tomorrow

    def generate_schedule_images(self):

        result = self.get_today_tomorrow_schedule()
        if not result:
            logger.debug("Object result not found")
            return None
        
        today_schedule, tomorrow_schedule, today, tomorrow = result
        
        today_image = self.create_schedule_image(today_schedule, today, "Сегодня")
        tomorrow_image = self.create_schedule_image(tomorrow_schedule, tomorrow, "Завтра")
        
        today_image.save("images/today_schedule.png")
        tomorrow_image.save("images/tomorrow_schedule.png")
        
        return "today_schedule.png", "tomorrow_schedule.png"



if __name__ == '__main__':

    group = "Б735"
    schedule_parser = ScheduleParserService(group_name=group)
    images_names = schedule_parser.generate_schedule_images()

    logger.info(f"Images generated. Names: {images_names}")
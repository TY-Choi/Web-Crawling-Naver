'''
Created on Jul 29, 2016

@author: TYchoi
'''
import excelHandler as excel
from PIL import Image
from selenium import webdriver
import urllib.request
import time

def image_loader(name):
    im = Image.open(name)
    pix = im.load()       
    width_length, height_length = im.size
    height_pix_list = []
    for height in range(height_length):
        width_pix_list1 = []
        width_pix_list2 = []
        contains_non_white = False
        for width in range(width_length):
            try:
                r,g,b = pix[width,height]
            except:
                r,g,b,a = pix[width,height]
            if r > 240 and g > 240 and b >240:
                width_pix_list1.append(width)
            elif r < 10 and g < 10 and b < 10:
                width_pix_list2.append(width)
            else:
                contains_non_white = True
            if contains_non_white:
                break
            if len(width_pix_list1) == width_length:
                height_pix_list.append(height)
            elif len(width_pix_list2) == width_length:
                height_pix_list.append(height)
                
    return height_length, height_pix_list

def define_non_white_region(height_length, height_pix_list):
    white_region = [0]
    for i in range(len(height_pix_list)-1):
        if height_pix_list[i+1]-height_pix_list[i] > 1:
                white_region.append(height_pix_list[i])
                white_region.append(height_pix_list[i+1])
    if len(white_region) % 2 == 1:
        white_region.append(height_pix_list[-1])
    
    if white_region[0] == 0:
        head_ends_at = white_region[1]
        white_region.remove(0)
        white_region.remove(head_ends_at)
        
    if white_region[-1] == height_length-1:
        footer_ends_at = white_region[-2]
        white_region.remove(white_region[-1])
        white_region.remove(footer_ends_at)
    return white_region

def get_number_of_cuts(white_region):
    refined_white_region = []
    for i in range(0,len(white_region),2):
        if white_region[i+1] - white_region[i] > 20:
            refined_white_region.append(white_region[i])
            refined_white_region.append(white_region[i+1])
    return int(len(refined_white_region)/2)+1

def count_cuts(url, driver, webtoon_id, episodeLinkNumber):
    driver.get(url)
    image_blocks = driver.find_element_by_css_selector('#toonLayer').find_elements_by_tag_name('img')
    sample_url = image_blocks[0].get_attribute('src').replace('001.jpg','')
    number_of_cuts = 0
    for i in range(1,len(image_blocks)-1):
        save_name = 'cutCounter/'+str(i)+'.jpg'
        number = '00' + str(i)
        if len(number) > 3:
            number = number[1:]
        img_url = sample_url+number+'.jpg'
        urllib.request.urlretrieve(img_url, save_name)
        save_name = 'cutCounter/'+str(i)+'.jpg'
        height_length, height_pix_list = image_loader(save_name)
        try :
            white_region = define_non_white_region(height_length, height_pix_list)
            number_of_cuts += get_number_of_cuts(white_region)
            crop_image(white_region, save_name, webtoon_id, episodeLinkNumber)
        except:
            number_of_cuts += 0
    return number_of_cuts

def crop_image(white_region, save_name,webtoon_id, episodeLinkNumber):
    im2 = Image.open(save_name)
    pix = im2.load()       
    width_length2, height_length2 = im2.size
    for i in range(1,len(white_region),2):
        if white_region[i+1] - white_region[i] > 30:
            im2.crop((0,white_region[i],width_length2,white_region[i+1])).save('splitted_images/'+webtoon_id+str(episodeLinkNumber)+str(i)+'.jpg')
            time.sleep(0.5)
        
def main():
    driver = webdriver.Chrome()
    cut_counts = count_cuts('http://m.comic.naver.com/webtoon/detail.nhn?titleId=20853&no=1052&weekday=tue', driver)
    print(cut_counts)
    driver.close()
if __name__ == "__main__":
    main()
    
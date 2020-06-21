import selenium.webdriver as webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import os
from six.moves.urllib.parse import urlparse
from bs4 import BeautifulSoup
import urllib.request
import time

#Being honest IDK how many of these imports are actually needed.

#Create a referal file, this may not be needed for you.
stora = open("StorageFile.txt","w+")

#Inform user what the wait is for
print("Starting Webdriver...")

#Start Moz Firefox in headless and assign driver.
os.environ['MOZ_HEADLESS'] = '1'
driver = webdriver.Firefox()

#Get URL, pray the user isn't stupid, make URL into a file name, make file with said name.
print("")
print("Make sure to include https:// at the start of the URL.")
print("")
#May be better to make it "input("https://www.instagram.com/ ")" to show what it works with.
url = input("PROFILE URL: ")
stora.write(url + '\n')
path = urlparse(url).path
FolderName = path.replace('/', '')
FolderPath = 'images/{}/'.format(FolderName)
if not os.path.exists(FolderPath):
	os.makedirs(FolderPath)
	
#Write to the referal file and open driver to the URL.
stora.write(os.getcwd() + FolderPath + '\n')
driver.get(url)

#Time for webpage to load.
time.sleep(2)

#Scroll all the way down the webpage to brign all images and video into source.
PauseTime = 2
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	time.sleep(PauseTime)
	new_height = driver.execute_script("return document.body.scrollHeight")
	if new_height == last_height:
		break
	last_height = new_height

#Using BS4 get the URL page's source.
soup = BeautifulSoup(driver.page_source, "lxml")

#Make coutners?
IsSame = 0
counter = 0
loca = 0

#For all HREF's in source do whatever this is.
for ob in soup.find_all("a"):
	loca = loca + 1
	image = str(ob["href"])
	counter = counter + 1
	
	#Print possible image URL to console for debug.
	print("IGNORE: " + image)
	
	#Very low quality skip of the stupid stuff that's the few first ones.
	if loca > 6:
		try:
		
			#Make a sharelink for each post to get the full res version of the image.
			sharelink = ("https://www.instagram.com" + image + "?utm_source=ig_web_copy_link")
			try:
				
				#Write the most recent post from the user to the referal file.
				if loca == 7:
					if not sharelink == stora.readline(3):
						IsSame = 1
						print("Link Updated")
						stora.write(sharelink+ '\n')
					else:
						IsSame = 0
						print("Link Same")
			except:
				break
			
			#Navigate the driver to the individual share links.
			driver.get(sharelink)
			
			#Wait for page content to load.
			time.sleep(1)
			
			#Run this mess again, checking for video content this time.
			soup = BeautifulSoup(driver.page_source, "lxml")
			for vid in soup.find_all("video"):
				Vids = str(vid["src"])
				
				#Print the resulting URL to the video.
				print(Vids)
				
				#Driver goes to original URL
				driver.get(url)
				
				#Wait for webpage to load
				time.sleep(1)
				try:
					
					#Set the resultign extension type.
					extension = ".mp4"
					try:
						if loca == 7:
							
							#Store the extension type to the referal file.
							stora.write(extension + '\n')
					except:
						break
						
					#Make the filename and save it.
					File_Name = FolderPath + str(counter) + extension
					urllib.request.urlretrieve(Vids, File_Name)
					print ("Video saved to disk as " + File_Name)
					
					#Check if the link was the same as before.
					if IsSame == 1:
						
						#Close referal file.
						stora.close()
				except:
				
					#If the page didn't have a video, complain.
					print("No")
					
			#Print sharelink for debugging.
			print (sharelink)
			
			#Assume since not video must be image.
			print ("Downloading image...")
			
			#I'll be hoenst I stole this part from stack overflow, I have no idea.
			#Think it finds the main image from the share link by checking meta tags.
			SHlink = urllib.request.urlopen(sharelink)
			htmlSource = SHlink.read()
			soup = BeautifulSoup(htmlSource,'html.parser')
			MetaTag = soup.find_all('meta', {'property':'og:image'})
			imgURL = MetaTag[0]['content']
			
			#Set the resulting extension type.
			extension = ".png"
			try:
				if loca == 7:
					
					#Store extension to referal file.
					stora.write(extension + '\n')
			except:
				break
			
			#Save image and inform user through console.
			File_Name = FolderPath + str(counter) + extension
			urllib.request.urlretrieve(imgURL, File_Name)
			print ("Image saved to disk as " + File_Name)
		except:
			
			#Dirty way of detecting the end.
			#The last link is "/legal/cookies" so it will error.
			#Using this error as a "feature" make it end the script.
			print ("All Images Proccessed...")
			print ("Proceeding To Exit...")
			
			
			driver.close()
			
			#Check if the link was the same as before.
			if IsSame == 1:
				
				#Close referal file.
				stora.close()
			break
			
#This seems to still only grab 30 or 31 posts, I can't work out why.
#But that seems more than enough for most people, if it becomes popular I'll perhaps fix it.
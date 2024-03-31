from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from multiprocessing import Process
import time

from tenacity import retry

# getDHLStatus():
# params:
# trkNum : an integer that represents the tracking number of the DHL package we are trying to track
# 
# 
def getDHLStatus(trkNum : int) -> list:
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.accept_insecure_certs = True
    driver = webdriver.Firefox(options=firefox_options)
    dhlLink = "https://www.dhl.com/us-en/home/tracking/tracking-express.html?submit=1&tracking-id="
    fullTrkNum = dhlLink + str(trkNum)
    driver.get(fullTrkNum)

    try:
        # Accepting cookies on the browser
        cookiesElement = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))
                                                        )
        driver.execute_script("arguments[0].click()", cookiesElement)

        # Hard coding a sleep timer to allow the DHL page to load the 3 seconds it requires
        time.sleep(4.5)
        
        # Attempting to click Track button
        trackElement = driver.find_element(By.XPATH, "/html/body/div[4]/main/div[1]/div[2]/div[1]/div/form/div/div/button")     
        ActionChains(driver).click(trackElement).perform()

        #-----#
        # time.sleep(2) # Uncomment if using the first results initialization
        # Getting the details of the status of the package
        # results = driver.find_elements(By.CLASS_NAME, "c-tracking-result--section")
        #-----#


        # Instead of hard coding a sleep timer, we wait until the presence of the elements are located
        try:
            results = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "c-tracking-result--section")))
        except:
            ActionChains(driver).click(trackElement).perform()
            results = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "c-tracking-result--section")))
        f = open("trackInfo" + ".txt", "a")
        info = str(trkNum) + "\n" + results[1].text + "\n"
        f.write(info)
        f.close()
        
        # info = [trkNum, results[1].text]
        # print("The info is " + str(info))
        # return info
        # driver.quit()
        
    finally:
        # creating a dictionary with key tracking number, and the results.
        # Appending it to listTrkNums, which is given to us
        # time.sleep(5)
        driver.quit()
        


# @retry((Exception), tries=3, delay=5, backoff=0)
# def getTrack(driver, trackElement):
#     try:
#             ActionChains(driver).click(trackElement).perform()
#             results = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "c-tracking-result--section")))
            
#     except:
#         if error_counter < 3:
#             error_counter += 1
#             getTrack(driver, trackElement)
#         raise Exception("Will not try again, have tried 3 times")  
#     error_counter = 0
#     return results



# going through each of the tracking numbers in successive order, one after the other
# for trkNum in listTrkNums:
#     getDHLStatus(trkNum)
if __name__ == '__main__':

    listTrkNums = []
    trkNum = None
    while trkNum != '':
        trkNum = input("Enter Tracking Number to find, enter blank to begin search: ")
        if trkNum != '':
            trkNum = int(trkNum)
            listTrkNums.append(trkNum)
    # infoTrkNums = []
    # Attempting to use Process package to run functions in parallel
    print("Looking up statuses for tracking numbers:")
    for i in listTrkNums:
        print(i)
    processes = []
    for trkNum in listTrkNums:
        p = Process(target=getDHLStatus, args=(trkNum,))
        processes.append(p)
        p.start()
        time.sleep(2)

    for p in processes:
        p.join()

    # print(processes)


    # driver.quit()

    # print(fullTrkNum)
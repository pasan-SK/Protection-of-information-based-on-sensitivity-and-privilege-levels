import csv
import hashlib
import getpass
from texttable import Texttable
import datetime

from urllib3 import Retry
user_records_file_name = "user_records.csv"
data_records_file_name = "data_records.csv"

#usernames and pwds
#Himal => ee
#patient1 => password1@A

#sensitivity levels for each record - 0, 1, 2 (if value if high => sensitivity is high)

# userTypes (also defines the priviledge levels):
# 0 - Patient - Can't read, write to data_records file
# 1 - administrationStaff - Can only read data records which has sensitivity level 0
# 2 - Nurse - Can read and write data records which has sensitivity level 0 or 1
# 3 - Doctor - Can read and write data records which has sensitivity level 0 or 1 or 2

def isValidPassword(pwd):

    # Minimum 8 characters.
    # The alphabet must be between [a-z]
    # At least one alphabet should be of Upper Case [A-Z]
    # At least 1 number or digit between [0-9].
    # At least 1 character from [ _ or @ or $ or # or * ].

    l, u, p, d = 0, 0, 0, 0
    if (len(pwd) >= 8):
        for i in pwd:

            # counting lowercase alphabets
            if (i.islower()):
                l+=1		

            # counting uppercase alphabets
            if (i.isupper()):
                u+=1		

            # counting digits
            if (i.isdigit()):
                d+=1		

            # counting the mentioned special characters
            if(i=='@'or i=='$' or i=='_' or i=='#' or i=='*'):
                p+=1		
    if (l>=1 and u>=1 and p>=1 and d>=1 and l+p+u+d==len(pwd)):
        return True
    else:
        return False

def readFromDataRecords(userType=0):
      
    # initializing the column-titles and rows list
    rows = []
    with open(data_records_file_name, 'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        
        # extracting field names through first row
        rows = [next(csvreader)]
        
        # extracting each data row one by one
        for row in csvreader:
            if (len(row) == 0):
                continue
            sensitivityLevelOfRecord = int(row[6])
            if (sensitivityLevelOfRecord < userType):
                rows.append(row)
        
        t = Texttable()
        t.add_rows(rows)
        print(t.draw())
        return rows

def writeToDataRecords(patientName, dateOfEntry, ageAtEnry, sicknessDetails, drugPrescriptions, labTestPrescriptions, sensitivityLevel):
    #checking whether there is a patient with the given patientName
    isFound = False
    with open(user_records_file_name, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
            if (len(row) == 0):
                continue
            if(row[0] == patientName and int(row[2]) == 0):
                isFound = True
                break

    if(isFound == False): return -1 # No patient found with the given patientName  

    # writing to csv file
    with open(data_records_file_name, 'a') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        # writing the data row
        csvwriter.writerow([patientName, dateOfEntry, ageAtEnry, sicknessDetails, drugPrescriptions, labTestPrescriptions, sensitivityLevel])

def registerUser(username, pwd, userType=0):  

    #checking whether there is a user with existing username
    fields = []
    rows = []
    with open(user_records_file_name, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
            if (len(row) == 0):
                continue
            if(row[0] == username):
                return -1 #return if a user with the given username is found

    #password hashing
    hashedPwd = hashlib.md5(pwd.encode()).hexdigest()

    # writing to csv file
    with open(user_records_file_name, 'a') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        # writing the data row
        csvwriter.writerow([username, hashedPwd, userType])

def readFromUserFile():
    # initializing the column-titles and rows list
    fields = []
    rows = []
    with open(user_records_file_name, 'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        
        # extracting field names through first row
        fields = next(csvreader)

        # extracting each data row one by one
        for row in csvreader:
            if (len(row) == 0):
                continue
            rows.append(row)

    # printing the field names
    print('Field names are:' + ', '.join(field for field in fields))

    # printing the content
    col_width = max(len(word) for row in rows for word in row) + 2  # padding
    print("".join(word.ljust(col_width) for word in ["username", "pwd", "userType"]))
    for row in rows:
        print("".join(word.ljust(col_width) for word in row))

def checkForUser(loggedUsername, loggedPassword):
    # initializing the column-titles and rows list
    fields = []
    rows = []
    with open(user_records_file_name, 'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        
        # extracting field names through first row
        fields = next(csvreader)

        # extracting each data row one by one
        for row in csvreader:
            if (len(row) == 0):
                continue
            if(row[0] == loggedUsername and row[1] == hashlib.md5(loggedPassword.encode()).hexdigest()):
                return {"username": loggedUsername, "userType": int(row[2])}
        return False

loggedUsername = str(input("Enter the username to login: ")).strip()
loggedPassword = getpass.getpass("Enter the password to login: ").strip()

loggeduser = checkForUser(loggedUsername, loggedPassword) 
if(loggeduser == False):
    print("Wrong username or password!")
else:
    print("\nSuccessfully logged in! - Welcome - " + loggeduser["username"])
    print("\nPlease select an option by entering the relevant number and then pressing 'enter' button\n\t1-register a user\n\t2-read data records\n\t3-insert data record")
    option = int(input("Enter the number: "))
    
    if(option == 1): # register user option
        if(loggeduser["userType"] == 0): # patient
            print("Sorry, patients cant create a user!")

        else:
            runLoop = True
            while runLoop:
                newUsername = input("\nenter the new username: ").strip()

                print("""\nNote: The password must be:
    Minimum 8 characters.
    The alphabet must be between [a-z]
    At least one alphabet should be of Upper Case [A-Z]
    At least 1 number or digit between [0-9].
    At least 1 character from [ _ or @ or $ or # or * ].""")

                newPassword = getpass.getpass("\nenter the new password: ").strip()
                
                if (isValidPassword(newPassword) == False ):
                    print("Invalid password!")
                    retry = int(input("Retry? \n\tenter 1 if you want to retry\n\tenter 0 if you want to cancel: \n").strip())
                    if(retry == 1):
                        continue
                    else:
                        print("GoodBye!")
                        runLoop = False
                        break
                else:
                    print("\nenter the userType: \n\t0 - Patient Level\n\t1 - administrationStaff\n\t2 - Nurse Level\n\t3 - Doctor")
                    newUserType = int(input("Enter the number: ").strip())
                    if(newUserType > loggeduser['userType']):
                        print("Sorry you cant create a user with a higher priviledge level than you!")
                        retry = int(input("Retry? \n\tenter 1 if you want to retry\n\tenter 0 if you want to cancel: \n").strip())
                        if(retry == 1):
                            continue
                        else:
                            print("GoodBye!")
                            runLoop = False
                            break
                    else:
                        result = registerUser(newUsername, newPassword, newUserType)  
                        if(result == -1):
                            print("Sorry the given username is already taken!")   
                            retry = int(input("Retry? \n\tenter 1 if you want to retry\n\tenter 0 if you want to cancel: \n").strip())
                            if(retry == 1):
                                continue
                            else:
                                print("GoodBye!")
                                runLoop = False
                                break
                        else:
                            print("Successfully added the user to the system!")
                            runLoop = False

    if(option == 2): #read data records

        if(loggeduser['userType'] == 0): # patient
            print("Sorry, patients don't have access to read the data!")

        else: result = readFromDataRecords(loggeduser['userType'])  

    if(option == 3): #insert a data record

        if (loggeduser['userType'] == 0): # patient
            print("Sorry, patients don't have access to insert data!")
        elif (loggeduser['userType'] == 1): # Administration staff member
            print("Sorry, Administration staff don't have access to insert data!")

        else: # logged user is either a nurse or a doctor at this point
            runLoop = True
            while runLoop:
                newRecordPatientName = str(input("enter a patient name: ").strip())
                try:
                    newRecordAgeAtEntry = int(input("enter a patient's current age (as an integer): ").strip())
                except:
                    print("Inavlid value for age!")
                    runLoop = False
                    break
                if (newRecordAgeAtEntry == ""): newRecordAgeAtEntry = "-"

                newRecordSicknessDetails = str(input("enter sickness details: ").strip())
                if (newRecordSicknessDetails == ""): newRecordSicknessDetails = "-"
                

                newDrugPrescriptions = str(input("enter drug prescriptions: ").strip())
                if (newDrugPrescriptions == ""): newDrugPrescriptions = "-"

                newLabPrescriptions = str(input("enter lab prescriptions: ").strip())
                if (newLabPrescriptions == ""): newLabPrescriptions = "-"

                try:
                    newRecordSensitivityLevel = int(input("enter sensitivity level (0, 1 or 2=highly sensitive): ").strip())
                    if(newRecordSensitivityLevel < loggeduser["userType"]):
                        result = writeToDataRecords(newRecordPatientName, datetime.datetime.now() ,newRecordAgeAtEntry, newRecordSicknessDetails, newDrugPrescriptions, newLabPrescriptions, newRecordSensitivityLevel)

                        if (result == -1):
                            print("Sorry, there is no patient with that username. Please add the patient first")
                            runLoop = False
                            break
                        else:
                            print("The data successfully recorded!")
                            runLoop = False
                            break
                    else:
                        print("Sorry, you don't have access to insert a data record with that sensitivity level!")   
                        retry = int(input("Retry? \n\tenter 1 if you want to retry\n\tenter 0 if you want to cancel: \n").strip())
                        if(retry == 1):
                            continue
                        else:
                            print("GoodBye!")
                            runLoop = False
                            break
                except:
                    print("Invalid input!")   
                    retry = int(input("Retry? \n\tenter 1 if you want to retry\n\tenter 0 if you want to cancel: \n").strip())
                    if(retry == 1):
                        continue
                    else:
                        print("GoodBye!")
                        runLoop = False
                        break
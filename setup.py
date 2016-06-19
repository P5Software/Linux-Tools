import socket
import fileinput
import shutil
import sys
import os.path

#Setup for P5Software linux tools
#Copyright 2016, P5Software, LLC

print '=================================='
print '+ P5 Software Linux Tools        +'
print '+ Initial Setup                  +'
print '=================================='

#define a reusable function with a default value
def default_input( message, defaultVal ):
    if defaultVal:
        return raw_input( "%s [%s]:" % (message,defaultVal) ) or defaultVal
    else:
        return raw_input( "%s " % (message) )

#Define variables the user doesn't get to modify
P5SoftwareHome="/etc/P5Software"
LinuxToolsHome=P5SoftwareHome+"/Linux-Tools"
configurationFile=LinuxToolsHome+"/s3cmd/s3cmd.conf"
s3IncludeFile=LinuxToolsHome+"/s3cmd/s3cmd.include"
s3ExcludeFile=LinuxToolsHome+"/s3cmd/s3cmd.exclude"
s3BucketName = ""

#Collect the required information from the user
serverHostname=default_input("Server Hostname?", socket.gethostname().upper())
serverFQDN=default_input("Server FQDN?", socket.getfqdn())

#Use the inverse of the FQDN as the default bucket name
s3BucketName_array = [x.strip() for x in serverFQDN.split('.')]

#Iterate through the FQDN to get the suggested S3 bucket name
i = len(s3BucketName_array)-1
while i > 0:
    s3BucketName = s3BucketName + s3BucketName_array[i] + "."
    i = i-1

#Append the hostname to the bucket name
s3BucketName = s3BucketName + serverHostname

s3BucketName=default_input("S3 Bucket?",s3BucketName.lower())
emailAddress=default_input("Confirmation E-Mail Address?","")
isDatabaseServer=default_input("Is this a MongoDB Server? (Y/N)", "N")
isDryRun=default_input("Enable Dry-Run? (Y/N)", "Y")
alreadyExists=default_input("Does this server already have a backup set in S3? (Y/N)", "N")

#Confirm the users' input
print '=================================='
print "Confirmation"
print '=================================='
print "Server Hostname: %s" % serverHostname
print "Server FQDN: %s" % serverFQDN
print "Amazon S3 Bucket Name: %s" % s3BucketName
print "Confirmation E-Mail Address: %s" % emailAddress
print "MongoDB Server: %s" % isDatabaseServer.upper()
print "Dry-Run Enabled: %s" % isDryRun.upper()
print "Server Already Exists in S3: %s" % alreadyExists.upper()

userConfirmed=default_input("Is this Correct (Y/N)?","Y")

#Replace the Y/N values with true/false values

if isDatabaseServer.upper() == "Y":
    isDatabaseServer="true"
else:
    isDatabaseServer="false"

if isDryRun.upper() == "Y":
    isDryRun="true"
else:
    isDryRun="false"

if alreadyExists.upper() == "Y":
    alreadyExists="true"
else:
    alreadyExists="false"

if userConfirmed.upper() != "Y":
    print "Destroying the input.  Run setup again to configure."
    sys.exit(1)

fsConfigurationFile = open( configurationFile, 'w')
fsConfigurationFile.write("serverHostname=%s\n" % serverHostname)
fsConfigurationFile.write("serverFQDN=%s\n" % serverFQDN)
fsConfigurationFile.write("s3BucketName=%s\n" % s3BucketName)
fsConfigurationFile.write("emailAddress=%s\n" % emailAddress)
fsConfigurationFile.write("isDatabaseServer=%s\n" % isDatabaseServer)
fsConfigurationFile.write("isDryRun=%s\n" % isDryRun)
fsConfigurationFile.write("alreadyExists=%s\n" % alreadyExists)
fsConfigurationFile.close()
    
#If the server doesn't already exist in S3, we can change the names of the include and exclude files
if alreadyExists == "true":
    
    print "Attempting to retrieve your existing s3cmd.include and s3cmd.exclude files..."
    
    #See if we are upgrading.  If so, copy the existing files from the legacy structure
    if os.path.isfile(P5SoftwareHome+"/s3cmd/s3cmd.include"):
        shutil.copy(P5SoftwareHome+"/s3cmd/s3cmd.include", s3IncludeFile)
        print "Upgraded your existing include file."
    else:
        print "Attempting to retrieve your existing include file from S3."
        os.system("sudo s3cmd get s3://" + s3BucketName + s3IncludeFile + " " + LinuxToolsHome + "/s3cmd/")

    if os.path.isfile(P5SoftwareHome+"/s3cmd/s3cmd.exclude"):
        shutil.copy(P5SoftwareHome+"/s3cmd/s3cmd.exclude", s3ExcludeFile)
        print "Upgraded your existing exclude file."
    else:
        print "Attempting to retrieve your existing exclude file from S3."
        os.system("sudo s3cmd get s3://" + s3BucketName + s3ExcludeFile + " " + LinuxToolsHome + "/s3cmd/")
    
else:
    shutil.move(s3IncludeFile+".example", s3IncludeFile)
    shutil.move(s3ExcludeFile+".example", s3ExcludeFile)

if os.path.isdir(P5SoftwareHome + "/s3cmd/"):
    print '*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*='
    print "An old version of P5Software's s3cmd scripts exists."
    print "After successfully executing a backup, you should delete the legacy tools."
    print "To delete them, run sudo rm -r " + P5SoftwareHome + "/s3cmd/
    print '*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*='
    print '\n'
    print '\n'

print '=================================='
print "Setup Complete"
print '=================================='
print "To execute a backup now, run sudo bash " + LinuxToolsHome + "/s3cmd/backup.sh\n\n"
print '\n'
sys.exit(0)
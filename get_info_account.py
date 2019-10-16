#!/usr/bin/python

#######################################################
# get_info_account(domain,path,ssl,cron) script for whm/cpanel
# Maxim Sasov  (maksim.sasov@hoster.by)
#######################################################

from datetime import datetime
import os, re,subprocess, sys, time
import simplejson as json
import socket

global search_account, now_time, domain, command_output, list_raw, list_account

userdata = '/etc/userdatadomains.json'
file_read = open(userdata).read()
list_raw = json.loads(file_read)
list_account=list_raw.keys()

search_account =''
now_time = datetime.now().strftime('%m-%d-%y-%H:%M:%S')


def info_domain(domain):
    domain_clean = ' '.join(domain.split())
    domain_clean = domain.strip()
    search_account = os.popen('/usr/local/cpanel/scripts/whoowns %s' %(domain_clean)).read()
    search_account = search_account.strip('\n')
    if len(search_account)==0:
        print('Domain ',domain,' not found on this server!')
        sys.exit()
    else:
        mysql_dump(search_account,domain)   
        
def mysql_dump(search_account,domain):
    cmd1 = ('cpapi2 --user=%s MysqlFE listdbs' %(search_account))
    PIPE = subprocess.PIPE
    command_process = subprocess.Popen(cmd1, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)
    command_output = command_process.communicate()[0]
    report(search_account,command_output,list_raw,domain)      


def report(search_account,command_output,list_raw,domain):
    report_account = open("%s(%s).%s" %(domain, search_account, now_time), "w")
    report_account.write("\n#-------------- Domain(s) and path(s) account %s ----------------#\n" %(search_account))
    for acc in list_account:
        if (list_raw[acc][0]) == search_account:
            report_account.write("\n[%s] [%s] -> %s\n\n" %(list_raw[acc][2], acc,list_raw[acc][4]))
            if os.path.exists("/var/cpanel/ssl/apache_tls/%s/combined" %(acc)):
                with open(r"/var/cpanel/ssl/apache_tls/%s/combined"%(acc), "r+") as f:
                    d = f.readlines()
                    f.seek(0)
                    for line in d:
                        report_account.write(line)
                    report_account.write('\n')
                f.close
    list_db_user =  re.findall(r'db:\s\w+\s+user:\s\w+', command_output)
    list_db_user = [x.replace(' ', '') for x in list_db_user]
    report_account.write("\n#-------------------- Databases ---------------------#\n\n%s\n\n" %(('\n'.join(list_db_user))))
    report_account.close()

try:
    argv1=sys.argv[1]
    info_domain(argv1)
except IndexError:
    print("No parametr")
    sys.exit (1)

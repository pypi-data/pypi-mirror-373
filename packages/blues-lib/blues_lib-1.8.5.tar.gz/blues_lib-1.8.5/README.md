## Description
Python library writed by Blues Liu.

[blues-lib](https://pypi.org/project/blues-lib/1.6.0/)

### pytest
```ps1
# windows
pytest tests/xx.test.ts

# macos
python3 -m pytest tests/xx.test.ts
```

### Install
install by requirements.txt
```
pip install -r requirements.txt
```


```
// first installation 
pip install blues-lib==1.3.14

// upgrade to the newest version
pip install --upgrade blues-lib
```

### sele
#### BluesDebugChrome

##### reliant env variables
1. `$env:CHROME_EXE` : the chrome's .exe file path - * required
  - such as `C:\Users\creep\AppData\Local\Google\Chrome\Application\chrome.exe`
2. `$env:CHROME_DRIVER_EXE` : the chromedriver's .exe file path - * recommended
  - such as `D:\devsoftware\Python38\webdriver\chrome\128.0.6613.86\chromedriver.exe`
3. `$env.LOGINER_EXECUTOR` : the loginer program path
  - dated setting: `D:\devapp\seleniumapp\loginer\Starter.py`

##### input
```py
config = {
  'url':'http://deepbluenet.com',
}
arguments = {
  '--user-data-dir':'"c:/sele/test3"',
  '--remote-debugging-address':'localhost:8003',
}
```


### util
```py
from blues_lib.util.BluesFiler import BluesFiler

print(BluesFiler.exists('dir'))
```

### set/get env variables
```
// set
[Environment]::SetEnvironmentVariable('LOGINER_EXECUTOR', 'D:\devapp\seleniumapp\loginer\Starter.py','machine')
// get
[Environment]::GetEnvironmentVariable('LOGINER_EXECUTOR','machine')
```

## QA

#### Selenium Wire CA error
```
ERROR:cert_verify_proc_builtin.cc(766)] CertVerifyProcBuiltin for at.alicdn.com failed:
----- Certificate i=1 (CN=Selenium Wire CA) -----
```

Resolve:
1. download ca.crt from selenium-wire library
```
https://github.com/wkeeling/selenium-wire/blob/master/seleniumwire/ca.crt
```

## Execute by powershell scheduled task
### task
```
unRegister-ScheduledTask -TaskName 'naps'
Get-ScheduledTask -TaskName 'naps'
Start-ScheduledTask -TaskName 'naps'
Get-ScheduledTaskInfo -TaskName 'naps'
enable-ScheduledTask -TaskName 'naps'
disable-ScheduledTask -TaskName 'naps'
```

### task in 24hours
```ps1
$arg='-NoProfile -command "& {set-location -path D:\devapp\pyapp\blues-lib-py\test\naps; python .\NAPSTest.py}"' ;  $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg ; 
$now = Get-Date ; 
$interval = New-TimeSpan -Hours 2; 
$trigger = New-ScheduledTaskTrigger -Once -RepetitionInterval $interval -At $now ; 
Register-ScheduledTask -Action $action  -Trigger $trigger -TaskName 'naps' 
```

### task in 7:00-23:00
```ps1
$arg = '-NoProfile -command "& {set-location -path D:\devapp\pyapp\blues-lib-py\test\naps; python .\NAPSTest.py}"'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg

$startTime = Get-Date -Hour 7 -Minute 0 -Second 0

$trigger = New-ScheduledTaskTrigger -Daily -At $startTime -RepetitionInterval (New-TimeSpan -Hours 2) -RepetitionDuration (New-TimeSpan -Hours 16)

Register-ScheduledTask -Action $action -Trigger $trigger -TaskName 'naps'
```

```ps1
# define the execute order
$arg='-NoProfile -command "& {set-location -path D:\devapp\pyapp\blues-lib-py\test\naps; python .\NAPSTest.py}"' ;  

# create task
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg ; 

$startTime = (Get-Date).Date.AddHours(7);
$interval = New-TimeSpan -Hours 2;
$endTime = (Get-Date).Date.AddHours(23);

# define the trigger
$trigger = New-ScheduledTaskTrigger -Daily -At $startTime -RepetitionInterval $interval -RepetitionDuration ($endTime - $startTime)

Register-ScheduledTask -Action $action  -Trigger $trigger -TaskName 'naps' 
```
### exe
```
$chrome="'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'" ; $arg='-NoProfile -command "& { set-location -path D:\datacross\dist\App; .\App.exe '+$chrome+' }"' ;  $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg ; $now = Get-Date ; $interval = New-TimeSpan -Hours 1; $trigger = New-ScheduledTaskTrigger -Once -RepetitionInterval $interval -At $now ; Register-ScheduledTask -Action $action  -Trigger $trigger -TaskName 'datacross' 
```

### install
This develop pc will push pip to officail reigstry ,can't set the mirros
```
pip install -i https://mirrors.aliyun.com/pypi/simple selenium
pip install -i https://mirrors.aliyun.com/pypi/simple --upgrade selenium
```


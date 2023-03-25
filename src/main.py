#!/bin/python
from __future__ import print_function, unicode_literals
from PyInquirer import prompt 
from pyfiglet import Figlet
import requests
from clint import arguments
from rich import print
import uuid
import subprocess

print("[yellow]{}[/yellow]".format(Figlet(font='slant').renderText('PipChecker')))

args = arguments.Args()
package = args.get(0)
if '==' in package:
    package_name = package.split('==')[0]
    package_version = package.split('==')[1]
else:
    package_name = package
    package_version = None

if package:
    print('[green]Package to be installed:[/green][bold blue] {0} [/bold blue]'.format(package))
else:
    print('[bold red]Please provide a package name[/bold red]')
    exit(1)

print('[green]Checking package in [/green][bold yellow]pypi[/bold yellow] [green]database...[/green]')
if package_version:
    req = requests.get("https://pypi.org/pypi/{0}/{1}/json".format(package_name,package_version))
else:
    req = requests.get("https://pypi.org/pypi/{0}/json".format(package_name))
if req.status_code == 404:
    print('[bold red]Package not found[/bold red]')
    exit(1)
pypi_package_data = req.json()
score = 10

# Print info to user
print('[bold green]Package found!![/bold green]')
print('[bold magenta]INFO:[/bold magenta]')
print('[bold blue]Package name:[/bold blue] {0}'.format(pypi_package_data['info']['name']))
print('[bold blue]Package version:[/bold blue] {0}'.format(pypi_package_data['info']['version']))
print('[bold blue]Package description:[/bold blue] {0}'.format(pypi_package_data['info']['summary']))
print('[bold blue]Package author:[/bold blue] {0}'.format(pypi_package_data['info']['author']))
print('[bold blue]Package license:[/bold blue] {0}'.format(pypi_package_data['info']['license']))
print('[bold blue]Package Homepage:[/bold blue] {0}'.format(pypi_package_data['info']['home_page']))

source = None
# Check if package has a repository available
if "github" in pypi_package_data['info']['home_page']:
    source = pypi_package_data['info']['home_page']
    print('[bold blue]Package Github:[/bold blue] {0}'.format(pypi_package_data['info']['home_page']))
elif "gitlab" in pypi_package_data['info']['home_page']:
    source = pypi_package_data['info']['home_page']
    print('[bold blue]Package Gitlab:[/bold blue] {0}'.format(pypi_package_data['info']['home_page']))  
elif "bitbucket" in pypi_package_data['info']['home_page']:
    source = pypi_package_data['info']['home_page']
    print('[bold blue]Package Bitbucket:[/bold blue] {0}'.format(pypi_package_data['info']['home_page']))
elif "github" in pypi_package_data['info']['project_urls'].get('Source',''):
    source = pypi_package_data['info']['project_urls'].get('Source','')
    print('[bold blue]Package Github:[/bold blue] {0}'.format(pypi_package_data['info']['project_urls']['Source']))
elif "gitlab" in pypi_package_data['info']['project_urls'].get('Source',''):
    source = pypi_package_data['info']['project_urls'].get('Source','')
    print('[bold blue]Package Gitlab:[/bold blue] {0}'.format(pypi_package_data['info']['project_urls']['Source']))
elif "bitbucket" in pypi_package_data['info']['project_urls'].get('Source',''):
    source = pypi_package_data['info']['project_urls'].get('Source','')
    print('[bold blue]Package Bitbucket:[/bold blue] {0}'.format(pypi_package_data['info']['project_urls']['Source']))
else:
    score -= 9
    print('[bold red]Package repository not found[/bold red]') 

# Check if package has known vulnerabilities
if pypi_package_data['vulnerabilities'] != []:
    print()
    print('[bold red]Package has vulnerabilities:[/bold red]')
    print()
    for vulnerability in pypi_package_data['vulnerabilities']:
        print()
        print('[bold red]Vulnerability CVE:[/bold red] {0}'.format(vulnerability['aliases'][0]))
        print('[bold red]Vulnerability ID:[/bold red] {0}'.format(vulnerability['id']))
        print('[bold red]Vulnerability description:[/bold red] {0}'.format(vulnerability['details']))
        print('[bold red]Vulnerability references:[/bold red] {0}'.format(vulnerability['link']))
        if vulnerability['fixed_in'] != []:
            print('[bold red]Vulnerability fixed in:[/bold red] [bold green] {0} [/bold green]'.format(vulnerability['fixed_in']))
    score -= 4
else:
    print()
    print('[bold green]Package has no known vulnerabilities[/bold green] !!')

#Synk static analysis
print()
print('[green]Checking package with [/green][bold magenta]Snyk static analysis[/bold magenta] [bold green]...[/bold green]')
print()
if source != None:
    tmp = uuid.uuid4()
    print('[green]Cloning repository...[/green]')
    gp = subprocess.Popen(["/usr/bin/git","-C","/tmp/".format(tmp),"clone","{}".format(source)])
    gp.communicate()
    print('[green]Running [magenta]Snyk[/magenta]... [/green]')
    p = subprocess.Popen(["/bin/snyk","code","test","-f","/tmp/{}".format(package_name)])
    p.communicate()
    if (p.returncode == 1):
        score -= 3

# Check if test cases pass
print()
print('[green]Checking package with [/green][bold magenta]pytest[/bold magenta] [bold green]...[/bold green]')
print()
if source != None:
    print('[green]Running [magenta]pytest[/magenta]... [/green]')
    # Create virtualenv in tmp directory
    subprocess.Popen(["/usr/bin/python3","-m","venv","/tmp/{}".format(tmp)]).communicate()
    # Install package in virtualenv
    subprocess.Popen(["/tmp/{}/bin/pip".format(tmp),"install","/tmp/{}".format(package_name)]).communicate()
    # Install pytest in virtualenv
    subprocess.Popen(["/tmp/{}/bin/pip".format(tmp),"install","pytest"]).communicate()
    # Run pytest in virtualenv
    p = subprocess.Popen(["/tmp/{}/bin/pytest".format(tmp),"/tmp/{}".format(package_name)])
    p.communicate()
    if (p.returncode == 1):
        score -= 3

print('[magenta]Package Score: [green] {} [/green] [/magenta]/ 13'.format(score))
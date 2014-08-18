from cloudmesh.util.gitinfo import GitInfo
from cloudmesh_common.logger import LOGGER
from flask import Blueprint, render_template
from flask.ext.login import login_required
from pprint import pprint, pprint
from sh import git
#import envoy
#import subprocess
import requests



log = LOGGER(__file__)

git_module = Blueprint('git_module', __name__)


@git_module.route('/git')
@login_required
def display_git_authors():
    result = git("shortlog", "-s", "-n",
                 _tty_in=True, _tty_out=False).split("\n")
    authors = {}
    for line in result:
        print line
        try:
            (commits, name) = line.split("\t")
            authors[name] = {"name": name, "commits": commits}
        except:
            print "error:", line

    #result = envoy.run('git log --all --format=\"%aN <%cE>\" | sort -u')
    #print result.std_out
    
    # Replacement of envoy by subprocess
    # git from sh does not respond due to unexpected issues.
    #p=subprocess.Popen(['git','shortlog','-e','-s'],stdout=subprocess.PIPE)
    #for line in p.stdout:
    #    print line

    """
    gitinfo = GitInfo()

    # print gitinfo.version()

    print "A"
    print gitinfo.authors()

    print "b"
    pprint(gitinfo.authors("dict"))

    print "c"
    pprint(gitinfo.emails())

    print "d"
    pprint(gitinfo.emails("dict"))

    print "e"
    pprint(gitinfo.info())

    print "f"
    print gitinfo.stat("laszewski@gmail.com")

    print "g"
    stats = gitinfo.compute()

    print stats

    print "h"
    for email in stats:
        p = stats[email]["percentage"]
        print "{0} {1:.3f}% {2:.3f}%  {3:.3f}% {4:.3f}%".format(email, p[0], p[1], p[2], p[3])
    """

    return render_template('general/git.html',
                           authors=authors)


@git_module.route('/bugs')
@login_required
def display_git_bugs():
    issues_open = requests.get('https://api.github.com/repos/cloudmesh/cloudmesh/issues?state=closed').json()
    issues_closed = requests.get('https://api.github.com/repos/cloudmesh/cloudmesh/issues?state=open').json()

    issues = issues_closed + issues_open

    return render_template('general/bugs.html',
                           issues=issues)




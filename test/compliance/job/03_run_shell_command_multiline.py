#!/usr/bin/env python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

__author__    = "Ole Christian Weidner"
__copyright__ = "Copyright 2012, Ole Christian Weidner"
__license__   = "MIT"

import sys
import getpass
import bliss.saga as saga

def run(url, username, queue, project):
    """Test if we can execute a regular executable that
        exists on the remote system.
    """
    try:
        ctx = saga.Context()
        ctx.context_type = saga.Context.SSH
        ctx.user_id  = username # like 'ssh username@host ...'

        js = saga.job.Service(url)
        js.session.contexts.append(ctx)

        # describe our job
        jd = saga.job.Description()

        jd.queue   = queue
        jd.project = project
        jd.wall_time_limit = 5 # minutes
 
        # environment, executable & arguments
        jd.environment = {'MYOUTPUT':'"Hello from Bliss"'}       
        jd.executable  = '/bin/bash'
        jd.arguments   = ['-c', 
"""\"
echo $MYOUTPUT
echo $MYOUTPUT
date
\""""]

        # output options
        jd.output = "bliss_job.03.stdout"
        jd.error  = "bliss_job.03.stderr"

        # create the job (state: New)
        myjob = js.create_job(jd)

        print "Job ID    : %s" % (myjob.job_id)
        print "Job State : %s" % (myjob.get_state())

        print "\n...starting job...\n"
        # run the job (submit the job to PBS)
        myjob.run()

        print "Job ID    : %s" % (myjob.job_id)
        print "Job State : %s" % (myjob.get_state())

        print "\n...waiting for job...\n"
        # wait for the job to either finish or fail
        myjob.wait()

        print "Job State : %s" % (myjob.get_state())
        print "Exitcode  : %s" % (myjob.exitcode)

        failed = False
        why = ""
        if myjob.get_state() != saga.job.Job.Done:
            failed = True
            why = "Job returned in state 'Failed'."

    except saga.Exception, ex:
        failed = True
        why = str(ex)

    if failed == True:
       print ""
       print "============================================"
       print "The job seems to have FAILED!"
       print "============================================"
       print "                                            "
       print "%s" % (why)
       print "Please run this test again with SAGA_VERBOSE=5 "
       print "and report the results at: "
       print ""
       print "https://github.com/saga-project/bliss/issues\n"

    else: 
      print ""
      print "============================================"
      print "The job seems to have executed successfully!"
      print "============================================"
      print "                                            "
      print "NOW, SOME MANUAL CHECKING IS REQUIRED!      "
      print "                                            "
      print "(1) Login to %s                             " % (url)
      print "(2) Make sure the file bliss_job.03.stdout exists"
      print "(3) Make sure bliss_job.03.stdout contains:"
      print "  Hello from Bliss" 
      print "  Hello from Bliss"
      print "  <The current date + time>"
      print ""
      print "If (1)-(3) are ok, this test can be considered as PASSED\n"

    return failed


def usage():
    print 'Usage: python %s ' % __file__
    print '                <URL>'
    print '                <REMOTEUSERNAME (default: local username)>'
    print '                <QUEUE (default: None)>'
    print '                <PROJECT (default: None)>'


def main():
    remoteusername = getpass.getuser()
    queue = None
    project = None
    js_url = None

    args = sys.argv[1:]
    if len(args) < 1:
        usage()
        sys.exit(-1)
    else:
        js_url = args[0]

    try:
        remoteusername = args[1]
        queue = args[2]
        project = args[3]
    except Exception:
        pass      

    return run(js_url, remoteusername, queue, project)


if __name__ == '__main__':
    sys.exit(main())


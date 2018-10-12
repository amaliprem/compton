#!/usr/bin/python
from subprocess import call
import sys, os, time, tarfile

def main():

#FIXME Update these
    email = "amali@jlab.org"

    config = "compton"

    identifier = raw_input("Please enter the identifier: ")
    energy = raw_input("Please enter the beam Energy (in MeV): ")
    runNr = raw_input("Please enter the run number: ")
    opticalBool = raw_input("Please enter the optical physics boolean (true or false): ")
    #val = raw_input("Please enter the varied parameter in cm: ")

    ## To print an xml file that allows for parameter space searches do this here
   # f = open('../geometry/'+identifier+'.xml', 'w')
   # fileout = '    <constant name="USShield1_increase_height" value="'+val+'"/>\n    <consant name="USShield2_increase_height" value"'+val+'"/>\n'
   # f.write(fileout)
   # f.close()

    #sourceDir = "/work/halla/parity/disk1/ciprian/prexSim"
    sourceDir = "/work/halla/parity/disk1/amali/gitdir/compton"
    outDir = "/lustre/expphy/volatile/halla/parity/amali/compton/"+identifier
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    nrEv   = 10 #1000
    nrStart= 0
    nrStopActual = 100
    nrStop = nrStopActual
#</FIXME>

    print('Running ' + str(nrEv*(nrStop - nrStart)) + ' events...')

    #jobName=config + '_' + identifier + '_' + val + "mm" + '_%03dkEv'%(nrEv/1000)
    jobName=config + '_' + identifier + '_energy_' + energy + 'MeV_runStart_' + runNr + '_%03dEv'%(nrEv)

    ###tar exec+geometry
    make_tarfile(sourceDir,config,identifier)

    for jobNr in range(nrStart,nrStop): # repeat for jobNr jobs
        print("Starting job setup for jobID: " + str(jobNr))

        jobFullName = jobName + '_%05d'%jobNr
        outDirFull=outDir+"/"+jobFullName
        createMacFiles(energy,opticalBool,config, outDirFull, sourceDir, nrEv, runNr, jobNr, identifier)

        ###copy tarfile
        call(["cp",sourceDir+"/workspace/z_config.tar.gz",
              outDir+"/"+jobFullName+"/z_config.tar.gz"])

    createXMLfile(sourceDir,outDir,jobName,runNr,nrStart,nrStop,email,identifier)

    print "All done for config ",config,"_",identifier," for #s between ",nrStart, " and ", nrStopActual


def createMacFiles(energy,opticalBool,config,outDirFull,sourceDir,nrEv,runNr,jobNr,identifier):

    if not os.path.exists(outDirFull+"/log"):
        os.makedirs(outDirFull+"/log")
    f=open(outDirFull+"/test_jaw.mac",'w')
    f.write("/Compton/gun/mode 3\n")
    f.write("/Compton/gun/verbose 0\n")
    f.write("/Compton/run/runnumber " + runNr + "\n")
    f.write("/Compton/run/autosave 1000\n")
    f.write("/Compton/gun/ElectronEnergy " + energy + " MeV\n")#1.95 GeV
    f.write("/Compton/gun/LaserWavelenght 532 nm\n")
    f.write("/Compton/gun/PhotonVertexZ 0.0 mm\n")
    f.write("/Compton/gun/Initialize\n")
    f.write("/Compton/event/printevent 10\n")
    f.write("/Compton/step/OpticalMaxStepTime 250 ns\n")
    f.write("/Compton/detector/setoptions :ALL_IGNORE: store_edep_hits=no\n")
    f.write("/tracking/verbose 0\n")
    f.write("/run/beamOn "+str(nrEv)+"\n")
    f.close()


    g=open(outDirFull+"/test_jaw.mac",'w')
    g.write("run=0\n")
    g.write("batch-file=test_jaw.mac\n")
    g.write("geometry-file=tst/geometries/ComptonGeometry.gdml\n")
    g.write("enable-optical="+opticalBool+"\n")
    g.write("rootfile-prefix=test\n")
    g.write("output-dir=./\n")
    g.write("\n")
    g.close()
    return 0

def createXMLfile(sourceDir,outDir,jobName,runNr,nrStart,nrStop,email,identifier):

    if not os.path.exists(sourceDir+"/workspace/jobs"):
        os.makedirs(sourceDir+"/workspace/jobs")

    f=open(sourceDir+"/workspace/jobs/"+jobName+".xml","w")
    f.write("<Request>\n")
    f.write("  <Email email=\""+email+"\" request=\"false\" job=\"true\"/>\n")
    f.write("  <Project name=\"prex\"/>\n")

#    f.write("  <Track name=\"debug\"/>\n")
#    f.write("  <Track name=\"analysis\"/>\n")
    f.write("  <Track name=\"simulation\"/>\n")

    f.write("  <Name name=\""+jobName+"\"/>\n")
    f.write("  <OS name=\"centos7\"/>\n")
    f.write("  <Memory space=\"3500\" unit=\"MB\"/>\n")

    f.write("  <Command><![CDATA[\n")
    f.write("    pwd\n")
    f.write("    tar -zxvf z_config.tar.gz\n")
    f.write("    ./ComptonG4_batch -c test.cfg\n")
    f.write("  ]]></Command>\n")

    for number in range(nrStart,nrStop): # repeat for nr jobs
        idName= outDir+"/"+jobName+'_%05d'%(number)
        f.write("  <Job>\n")
        f.write("    <Input src=\""+idName+"/z_config.tar.gz\" dest=\"z_config.tar.gz\"/>\n")
        f.write("    <Input src=\""+idName+"/test_jaw.mac\" dest=\"test_jaw.mac\"/>\n")
        f.write("    <Input src=\""+idName+"/test.cfg\" dest=\"test.cfg\"/>\n")
	runNr5='%05d'%(int(runNr))
        f.write("    <Output src=\"test"+runNr5+".root\" dest=\""+idName+"/test"+runNr5+".root\"/>\n")
        f.write("    <Stdout dest=\""+idName+"/log/log.out\"/>\n")
        f.write("    <Stderr dest=\""+idName+"/log/log.err\"/>\n")
        f.write("  </Job>\n\n")

    f.write("</Request>\n")
    f.close()
    return 0

def make_tarfile(sourceDir,config,ident):
    print "making geometry tarball"
    if os.path.isfile(sourceDir+"/workspace/z_config.tar.gz"):
        os.remove(sourceDir+"/workspace/z_config.tar.gz")
    tar = tarfile.open(sourceDir+"/workspace/z_config.tar.gz","w:gz")
    #tar.add(sourceDir+"/build/ComptonG4_batch",arcname="ComptonG4_batch")
    tar.add(sourceDir+"/workspace/tst",arcname="tst")

    tar.close()

if __name__ == '__main__':
    main()


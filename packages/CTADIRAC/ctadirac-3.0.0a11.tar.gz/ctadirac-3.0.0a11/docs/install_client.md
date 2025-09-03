# Install CTADIRAC client

Install the CTADIRAC client to use the CTADIRAC certification instance:

https://majestix-vm3.zeuthen.desy.de/DIRAC

## Prerequisites

Have a grid certificate and be registered to the CTA Virtual Organization:

https://cclcgvomsli01.in2p3.fr:8443/voms/vo.cta.in2p3.fr/

## Installation

On a Linux platform:

```
curl -LO https://github.com/DIRACGrid/DIRACOS2/releases/latest/download/DIRACOS-Linux-x86_64.sh
bash DIRACOS-Linux-x86_64.sh
```

On a MacOS platform:

```
curl -LO https://github.com/DIRACGrid/DIRACOS2/releases/latest/download/DIRACOS-Darwin-x86_64.sh
bash DIRACOS-Darwin-x86_64.sh
```

Then:

```
source diracos/diracosrc
pip install CTADIRAC
```

## Configuration

Only the first time:

```
source diracos/diracosrc
pip install CTADIRAC
dirac-cert-convert <USERCERT>.p12
dirac-configure -C https://majestix-vm1.zeuthen.desy.de:9135/Configuration/Server -S CTADIRAC-alma
```

## Run test jobs

Get a proxy valid 24 hours:

`dirac-proxy-init`

### Submit a hello world job

`git clone https://gitlab.cta-observatory.org/cta-computing/dpps/workload/CTADIRAC.git`

`cd CTADIRAC/docs/examples`

`python testJob.py`

### Submit a MC simulation job

`cd CTADIRAC/docs/examples`

`cta-prod-submit testJob mc_example.yml wms`

To run test jobs at a specific site, edit `mc_example.yml` and set:

`destination: <site>`

where site is among:

`CTAO.PIC.es`
`CTAO.FRASCATI.it`
`CTAO.DESY-ZEUTHEN.de`
`CTAO.CSCS.ch`

or a list of sites, e.g.: `["CTAO.DESY-ZEUTHEN.de", "CTAO.CSCS.ch"]`

### Submit a processing job

`cd CTADIRAC/docs/examples`

`cta-prod-submit testJob dl0_to_dl2_example.yml wms`

### Monitor jobs

Check your jobs here:

https://majestix-vm3.zeuthen.desy.de/DIRAC

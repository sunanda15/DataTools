// C++ includes
#include <iostream>
#include <stdlib.h>
#include <vector>

//ROOT Includes
#include "TH1F.h"
#include "TH2F.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TFile.h"
#include "math.h"
#include "TSpectrum2.h"
#include "TCanvas.h"
#include "TRandom.h"
#include "TH2.h"
#include "TF2.h"
#include "TMath.h"
#include "TROOT.h"
#include "TClonesArray.h"
#include "TObject.h"

//WCSim Includes
#include "WCSimRootEvent.hh"
#include "WCSimRootGeom.hh"
#include "WCSimRootLinkDef.hh"

//Definitions
#define PI 3.141592654
#define GridX 20350 // This is the half-width of the grid which will divide the unfolded cylinder 
#define GridY 10000 // This is the half-length of the grid which will divide the unfolded cylinder
#define GridXBin 40 // The number of bins in the horizontal
#define GridYBin 20 // The number of bins in the vertical
/*
*How to run:
*
* enter in the terminal root -l llib.C 'digihit_charge_quality.C("WCSim.root","outputFile.root",false)' to run the code
* where you replace WCSim.root with your file name and outputfile with the name you wish to save it under
*/

// a structure to hold a pmt id along with its charge
typedef struct
{
  double charge;
  double id;
} pmt;

// a structure to hold the details of each grid point
typedef struct
{
  double charge;
  int xbin;
  int ybin;
  double x;
  double y;
  double z;
  double totCharge;
} section;

// ====================================================================================

void ODAnalysis( const char *inFileName = "wcsim.root",
                 const char *outFileName = "Hits.root", 
                 bool verbosity = 0)
{
  bool createCanvases = false;

  // Some nice formatting for text options
  std::cout << std::scientific; //all numbers appear in scientific notation
  std::cout << std::setprecision(2); //sets all numbers to output to no more than 2 D.P.
  std::cout << std::left; // Sets the text justification to the left
  const int txtW = 20; // Width of box 'holding' text
  const int numW = 10; // Width of box 'holding' numbers

  // Open the WCSim file
  TFile *inFile = new TFile(inFileName, "READ");
  if ( !inFile->IsOpen() )
    std::cout << "Error: Could not open file \"" << inFileName << "\"." <<std::endl;
  else if (verbosity)
    std::cout << "Input file: " << inFileName << std::endl;

	// Get a pointer to the tree from the input file
	TTree *wcsimTree = (TTree*) inFile->Get("wcsimT");

	// Get the number of events in the tree
	long int nEvent = wcsimTree->GetEntries();
	if (verbosity)
    std::cout << "Number of events: "<< nEvent << std::endl;

	// Create a WCSimRootEvent to put stuff from the tree in
	WCSimRootEvent *wcsimRoot_3 = new WCSimRootEvent();
	WCSimRootEvent *wcsimRoot_20 = new WCSimRootEvent();

	//ID Event readings
	TBranch *branch_20 = wcsimTree->GetBranch("wcsimrootevent");
	branch_20->SetAddress(&wcsimRoot_20);

	//Force Deletion to prevent memory leak
	wcsimTree->GetBranch("wcsimrootevent")->SetAutoDelete(kTRUE);

	//3 in PMT readings and branch creation

	// Set the branch address for reading from the tree
	TBranch *branch_3 = wcsimTree->GetBranch("wcsimrootevent2");
	branch_3->SetAddress(&wcsimRoot_3);

	// Force deletion to prevent memory leak
	wcsimTree->GetBranch("wcsimrootevent2")->SetAutoDelete(kTRUE);

	// Load the geometry tree (only 1 "event")
	TTree* geoTree = (TTree*) inFile->Get("wcsimGeoT");
	WCSimRootGeom *geo = 0;
	geoTree->SetBranchAddress("wcsimrootgeom", &geo);
	if (verbosity)
   std::cout << "Geotree has " << geoTree->GetEntries() << " entries." << std::endl;
	geoTree->GetEntry(0);

	// Start with the main trigger as it always exists and contains most of the info
	WCSimRootTrigger *wcsimTrigger_20;
	WCSimRootTrigger *wcsimTrigger_3;

  // Define objects that holds hit time info
  WCSimRootCherenkovHitTime *wcsimCherenkovHitTime_20;
  WCSimRootCherenkovHitTime *wcsimCherenkovHitTime_3;

	// Create an output file
	TFile *outFile = new TFile(outFileName, "RECREATE");
  TTree *totalTree = new TTree("totalTree", "total info")
	TTree *Tree_20 = new TTree("Tree_20", "20in info");
  TTree *Tree_3 = new TTree("Tree_3", "3in info");

  // Create branches for the tree
  int ev; // Event number
  Float_t totalDigiQ;
  Float_t maxDigiQ_20;
  Float_t maxDigiQ_3;
  // Variables for total hits and charge
  int totalDigiHit;
  double totalQ;
  // Branch for ID info
  std::vector<int>    tubeID_20;
  std::vector<double> digiHitT_20;
  std::vector<double> digiHitQ_20;
  // Branch for OD info
  std::vector<int>    tubeID_3;
  std::vector<double> digiHitT_3;
  std::vector<double> digiHitQ_3;

  totalTree->Branch("totalDigiQ", &totalDigiQ, "totalDigiQ/F");
  totalTree->Branch("maxDigiQ_20", &maxDigiQ_20, "maxDigiQ_20/F");
  totalTree->Branch("maxDigiQ_3", &maxDigiQ_3, "maxDigiQ_3/F");
  totalTree->Branch("totalDigiHit", &totalDigiHit, "totalDigiHit/F");
  totalTree->Branch("totalQ", &totalQ, "totalQ/F");

  Tree_20->Branch("EvtNum", &ev, "ev/I");
  Tree_20->Branch("tubeID", &tubeID_20);
  Tree_20->Branch("digiHitT", &digiHitT_20);
  Tree_20->Branch("digiHitQ", &digiHitQ_20);

  Tree_3->Branch("EvtNum", &ev, "ev/I");
  Tree_3->Branch("tubeID", &tubeID_3);
  Tree_3->Branch("digiHitT", &digiHitT_3);
  Tree_3->Branch("digiHitQ", &digiHitQ_3);

	// Detector Geometry Details
	int MAXPMT_20 = geo->GetWCNumPMT(0); //Get the maximum number of PMTs in the ID
	int MAXPMT_3 = geo->GetWCNumPMT(1); //Get the maximum number of PMTs in the OD

	// loop over events
	for (ev = 0; ev < nEvent; ev++)
  {
	  wcsimTree->GetEntry(ev);

    tubeID_20.clear();
    digiHitT_20.clear();
    digiHitQ_20.clear();
    tubeID_3.clear();
    digiHitT_3.clear();
    digiHitQ_3.clear();
    totalDigiQ = 0.;
    maxDigiQ_20 = 0.;
    maxDigiQ_3 = 0.;
    totalDigiHit = 0;
    totalQ = 0;

    // ID related
    wcsimTrigger_20 =  wcsimRoot_20->GetTrigger(0);
    int numTriggers_20 = wcsimRoot_20->GetNumberOfEvents();
    int numSubTriggers_20 = wcsimRoot_20->GetNumberOfSubEvents();

    // OD related
	  wcsimTrigger_3 = wcsimRoot_3->GetTrigger(0);
	  int numTriggers_3 = wcsimRoot_3->GetNumberOfEvents();
	  int numSubTriggers_3 = wcsimRoot_3->GetNumberOfSubEvents();

    // loop for ID
    for (int iTrig_20 = 0; iTrig_20 < numTriggers_20; ++iTrig_20)
    {        
      wcsimTrigger_20 = wcsimRoot_20->GetTrigger(iTrig_20);
      int numTracks_20 = wcsimTrigger_20->GetNtrack();

      int numPMTsDigiHit_20 = wcsimTrigger_20->GetNcherenkovdigihits();
      double totalQ_20 = wcsimTrigger_20->GetSumQ();

      // Plot histos for digitised hits
      totalDigiHit += numPMTsDigiHit_20;
      // digiHitHistoID->Fill(numPMTsDigiHit_20);
      totalQ += totalQ_20;

      // loop through digitised hits to get time and charge information
      for (int idigiHit = 0; idigiHit < numPMTsDigiHit_20; ++idigiHit)
      {
        WCSimRootCherenkovDigiHit *aDigiHit =
            (WCSimRootCherenkovDigiHit*)wcsimTrigger_20->GetCherenkovDigiHits()->At(idigiHit);
        float charge = aDigiHit->GetQ();
        // Store info in tree
        tubeID_20.push_back(aDigiHit->GetTubeId());
        digiHitT_20.push_back(aDigiHit->GetT());
        digiHitQ_20.push_back(charge);
        totalDigiQ += charge;
        if( charge > maxDigiQ_20) maxDigiQ_20 = charge;
      } // end of digitised hit loop
    } // end of ID trigger loop

    // loop for OD
	  for (int nTrig_3 = 0; nTrig_3 < numTriggers_3; ++nTrig_3)
    {
	  	wcsimTrigger_3 = wcsimRoot_3->GetTrigger(nTrig_3);
	  	int numTracks_3 = wcsimTrigger_3->GetNtrack();

      int numPMTsDigiHit_3 = wcsimTrigger_3->GetNcherenkovdigihits();
      double totalQ_3 = wcsimTrigger_3->GetSumQ();

      // Plot histos for digitised hits
      totalDigiHit += numPMTsDigiHit_3;
      totalQ += totalQ_3;

      // loop through digitised hits to get time and charge information
      for (int idigiHit = 0; idigiHit < numPMTsDigiHit_3; ++idigiHit)
      {
        WCSimRootCherenkovDigiHit *aDigiHit =
            (WCSimRootCherenkovDigiHit*)wcsimTrigger_3->GetCherenkovDigiHits()->At(idigiHit);
        float charge = aDigiHit->GetQ();
        // Store info in tree
        tubeID_3.push_back(aDigiHit->GetmPMT_PMTId());
        digiHitT_3.push_back(aDigiHit->GetT());
        digiHitQ_3.push_back(charge);
        totalDigiQ += charge;
        if( charge > maxDigiQ_3) maxDigiQ_3 = charge;
      }// End of loop over digi hits
	  } // End of OD trigger loop

    totalTree->Fill();
    Tree_20->Fill();
    Tree_3->Fill();
	} // end of event loop

  totalTree->Write();
	Tree_20->Write(); // Write tree to the output file.
  Tree_3->Write();
	outFile->Close(); // Close the output file.
}

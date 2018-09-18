void eDep_gammaE(){
  EColor colorarray[9]={kPink,kOrange-3,kYellow-1,kGreen,kCyan+2,kAzure-3,kBlue-10,kViolet-6,kMagenta};
  TCanvas* c1 = new TCanvas("c1","c1",700,500);
  TFile *f = TFile::Open("ComptonG4_tungsten_10617_100000.root");
  TTree* tree = (TTree*) f->Get("ComptonG4");
  TProfile* h = new TProfile("h","h",100,0,3000,0,3000);
  ComptonG4->SetTitle("energy deposited in tungsten jaw");
  ComptonG4->Draw("phys_jaw_eDep/gammaE:gammaE");
  //ComptonG4->SetTitle("energy deposited in tungsten jaw");
  Double_t jaw_eDep, gammaE;
  tree->SetBranchAddress("phys_jaw_eDep", &jaw_eDep);
  tree->SetBranchAddress("gammaE",&gammaE);

  for (int i=0;i<tree->GetEntries();i++){
    tree->GetEntry(i);
    h->Fill(gammaE,jaw_eDep/gammaE);  
  }
  TCanvas* c2 = new TCanvas("c2","c2",700,500);
  h->SetMarkerColor(kRed);
  //h->SetLineColor(10);
  h->SetMarkerStyle(7);
  h->SetTitle("energy deposited in tungsten jaw;gammaE;eDep");  
  h->Draw("P");

}

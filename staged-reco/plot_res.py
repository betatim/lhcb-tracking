import ROOT as R

R.gROOT.SetBatch(True)
R.gROOT.ProcessLine(".x lhcbstyle2.C")
R.TH1.SetDefaultSumw2(True)


track_type = "Long"

# HLT plus to get to offline efficiency
files = [("offline-res-10000ev-histos.root",
          (R.kBlack,20), "offline"),
         ("hlt-offline-all_velo_LHCbID-10000ev-histos.root",
          (R.kRed,22), "HyperLoop"),
         ("hlt-offline-test-10000ev-histos.root",
          (R.kBlue,24), "HyperLoop+offline fit"),
         #("hlt-offline-test-10000ev-histos2.root",
         # (R.kBlue,25), "HyperLoop+offline fit2"),
         ("hlt-offline-addTT-3000ev-histos3.root",
          (R.kBlue, 26), "HyperLoop+offline fit+addTT"),
         ("hlt-offline-addTT-3000ev-histos4.root",
          (R.kGreen, 25), "HyperLoop+fast fit+addTT"),
         #("hlt-offline-fitter-no-material-addTT-3000ev-histos5.root",
         # (R.kGreen, 27), "HyperLoop+offline fit(simple material)+addTT"),
]
prefix = "Res_%s_"%(track_type)

files = [("offline-res-10000ev-histos.root", (R.kBlack,20), "offline"),
         ("hlt-plus-offline-final-10000ev-histos.root",
          (R.kRed,29), "HLT+"),
]
prefix = "Res_HLT2015hyper_%s_"%(track_type)

files = [("offline-res-10000ev-histos.root", (R.kBlack,20), "offline"),
         ("t/hlt-plus-offline-only-unused-velo-tracks-markLHCbIDs-10000ev-histos.root",
          (R.kRed,29), "unused-marked"),
         ("t/hlt-plus-offline-all-velo-tracks-markLHCbIDs-10000ev-histos.root",
          (R.kBlue,28), "all-marked"),
         ("t/hlt-plus-offline-only-unused-velo-tracks-10000ev-histos.root",
          (R.kGreen,27), "unused-unmarked"),
         ("t/hlt-plus-offline-all-velo-tracks-10000ev-histos.root",
          (R.kCyan,26), "all-unmarked"),
         ("hlt-plus-offline-unused-velo-tracks-unused-hits-addTTInFwd2-1000ev-histos.root",
          (R.kOrange,25), "t"),
]
prefix = "Res_test_%s_"%(track_type)

xlabels = {"Pt": "Pt [MeV]",
           "P": "P [MeV]",
           "3": "#chi^{2}/ndof",
           "4": "#LHCbIDs",
           "110": "#TT hits",
           "111": "#IT hits",
           "112": "#OT hits",
           "dpoverp_vs_p": "P [GeV]",
       }
ylabels = {"dpoverp_vs_p": "dp/p",
}


def monitor_plots(tfile, plots, histos=("4", "110", "111", "112",
                                        "OTResidual",
                                        "ITResidual",
                                        "TTResidual",
                                        "multiplicity",
                                        "3",
                                    )):
    tfile.cd("Track/TrackMonitor/%s"%(track_type))
    Dir = R.gDirectory
    get = Dir.Get
    
    for h_name in histos:
        h = get(h_name)
        #print h_name, h
        if h:
            #print h_name, h.Integral()
            h.Scale(1./h.Integral())
            plots.append(h)
            h.GetXaxis().SetTitle(xlabels.get(h_name, h_name))

def res_plots(tfile, plots,
              histos=("xpull", "ypull",
                      "txpull", "typull",
                      "qoppull", "ppull",
                      "dpoverp"
                  ),
              profiles=("dpoverp_vs_p",)):
    tfile.cd("Track/TrackResChecker/%s/vertex"%(track_type))
    Dir = R.gDirectory
    get = Dir.Get
    
    for h_name in histos:
        h = get(h_name)
        #print h_name, h
        if h:
            #print h_name, h.Integral()
            plots.append(h)
            if ("pull" in h_name or
                "Residual" in h_name):
                h.Scale(1./h.Integral())

            h.Scale(1./h.Integral())
                
            h.GetXaxis().SetTitle(xlabels.get(h_name, h_name))

    for h_name in profiles:
        h2d = get(h_name)
        if h2d:
            h2d.FitSlicesY()
            h = get(h_name + "_2")
            h.GetXaxis().SetTitle(xlabels.get(h_name, h_name))
            h.GetYaxis().SetTitle(ylabels.get(h_name, h.GetYaxis().GetTitle()))
            if h_name == "dpoverp_vs_p":
                h.GetYaxis().SetRangeUser(0, 0.008)
                
            plots.append(h)


c = R.TCanvas("", "", 615,615)
c.SetRightMargin(0.1)

plots = {}
for fname, colour, name in files:
    plots[name] = []

open_files = []

for fname, colour, name in files:
    print fname, "="*40
    tf = R.TFile(fname)
    open_files.append(tf)

    Dir = R.gDirectory
    get = Dir.Get

    monitor_plots(tf, plots[name])
    res_plots(tf, plots[name])


for fname, (colour,shape), name in files:
    for plot in plots[name]:
        plot.SetLineColor(colour)
        plot.SetMarkerColor(colour)
        plot.SetMarkerStyle(shape)

names = [n[2] for n in files]
# Find a suitable y range
for n,_ in enumerate(plots[names[0]]):
    maxy = -1
    for name in names:
        plot = plots[name][n]
        maxy_ = plot.GetBinContent(plot.GetMaximumBin()) * 1.1
        if maxy_ > maxy:
            maxy = maxy_

    for name in names:
        plot = plots[name][n]
        plot.GetYaxis().SetRangeUser(0., maxy)

for n,plot in enumerate(plots[names[0]]):
    plot.Draw("PE")
    leg = R.TLegend(0.85,0.89,1,1)
    leg.AddEntry(plot, names[0])
    
    for name in names[1:]:
        plot_ = plots[name][n]
        plot_.Draw("PEsame")
        leg.AddEntry(plot_, name)

    leg.Draw()
    c.SaveAs(prefix + plot.GetName() + ".pdf")

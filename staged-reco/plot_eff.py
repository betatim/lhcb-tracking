import ROOT as R

R.gROOT.SetBatch(True)
R.gROOT.ProcessLine(".x lhcbstyle2.C")
R.TH1.SetDefaultSumw2(True)


#track_type = "Upstream"
#track_type = "Best"
#track_type = "Velo"
#track_type = "Forward"
track_type = "BestLong"
#track_type = "Downstream"
#track_type = "Match"
#track_type = "TTrack"

# HLT only comparison
files = [("offline-10000ev-histos.root", (R.kBlack,20), "offline"),
         ("full-hlt-10000ev-histos.root", (R.kBlue,22), "HLT"),
         #("hlt-plus-offline-10000ev-histos.root", (R.kGreen,23), "HLT+"),
]
prefix = "HLT2015_%s_"%(track_type)
# HLT plus to get to offline efficiency
#files = [("offline-10000ev-histos.root", (R.kBlack,20), "offline"),
#         ("full-hlt-plus-offline-10000ev-histos.root", (R.kRed,22), "HLT+"),
#         ("full-hlt-plus-offline-recycling-10000ev-histos.root", (R.kBlue,24), "HLT++"),
#]
#prefix = "HLT2015plus_%s_"%(track_type)

# tracking meeting 2.10.2014
#files = [("offline-10000ev-histos.root", (R.kBlack,20), "offline"),
#         ("full-hlt-plus-offline-recycling-10000ev-histos.root",
#          (R.kBlue,24), "HLT+"),
#         ("hlt-offline-all_velo_LHCbID-10000ev-histos.root",
#          (R.kRed,22), "HLT+veto"),
#]
#prefix = "HLT2015hyper_%s_"%(track_type)

files = [("offline-res-10000ev-histos.root", (R.kBlack,20), "offline"),
         ("hlt-plus-offline-final-10000ev-histos.root",
          (R.kRed,29), "HLT+"),
]
prefix = "HLT2015hyper_%s_"%(track_type)


ylabels = {"Pt": "Pt [MeV]", "P": "P [MeV]"}

def ghost_plots(plots,
                variables=("Eta", "Pt", "Phi", "P", "nPV")):
    for var in variables:
        h = get("%s_Ghosts"%var)
        if not h:
            continue

        #h.Scale(1./h.Integral())
            
        plots.append(h)
        h.GetXaxis().SetTitle(ylabels.get(var, var))
        h.GetYaxis().SetRangeUser(0, 1.1 * h.GetBinContent(h.GetMaximumBin()))

def make_plots(category, plots,
               variables=("Eta", "Pt", "Phi", "P", "expectedHits",
                          "PVz", "nPV", "docaz", "ThetaX", "ThetaY"),
               ylimits=(0.8, 1.05)):
    for var in variables:
        recon = get("%s_%s_reconstructible"%(category, var))
        recod = get("%s_%s_reconstructed"%(category, var))

        # not all histograms exist for all track types
        if not recon:
            continue
        
        if var == "docazXXX":
            recon.Rebin(2)
            recod.Rebin(2)
            
        ratio = recon.Clone("%s_ratio_%s"%(category, var))
        plots.append(ratio)
        
        ratio.Divide(recod, recon, 1,1,"b")
        #print name, category, var, ratio.Integral()
        
        ratio.GetXaxis().SetTitle(ylabels.get(var, var))
        ratio.GetYaxis().SetRangeUser(*ylimits)
        ratio.GetYaxis().SetTitle("recod/reconstructible")
        if var == "PtXXX":
            ratio.GetXaxis().SetRangeUser(0, 5000)

c = R.TCanvas("", "", 615,615)
c.SetRightMargin(0.1)

plots = {}
for fname, colour, name in files:
    plots[name] = []

open_files = []

for fname, colour, name in files:
    tf = R.TFile(fname)
    open_files.append(tf)

    tf.cd("Track/PrChecker/%s"%track_type)

    Dir = R.gDirectory
    get = Dir.Get

    ylimits = (0.8, 1.05)
    if track_type == "Forward":
        ylimits = (0.5, 1.0)
    elif track_type in ("Upstream", "Match"):
        ylimits = (0., 1.0)

    ylimits = (0., 1.05)
    #make_plots("velo", plots[name], ylimits=ylimits)
    make_plots("long", plots[name], ylimits=ylimits)
    make_plots("long>5GeV", plots[name], ylimits=ylimits)
    make_plots("long_fromB", plots[name], ylimits=(0.,1.05))
    make_plots("long_fromB>5GeV", plots[name], ylimits=ylimits)
    #make_plots("UT_long_fromB_P>3GeV_Pt>0.5GeV", plots[name], ylimits=ylimits)
    make_plots("long_fromB_P>3GeV_Pt>0.5GeV", plots[name], ylimits=ylimits)
    make_plots("noVelo+UT+T_strange", plots[name], ylimits=(0., 1.05))

    ghost_plots(plots[name])

for fname, (colour,shape), name in files:
    for plot in plots[name]:
        plot.SetLineColor(colour)
        plot.SetMarkerColor(colour)
        plot.SetMarkerStyle(shape)

names = [n[2] for n in files]
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

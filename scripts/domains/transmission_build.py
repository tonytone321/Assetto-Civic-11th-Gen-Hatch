import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import dbutil as db
T=db.load_or_new("transmission","Transmission")
T["sources"]={}; T["parameters"]={}
db.add_source(T,"tx:hondanews-us-2024-hatch-specs","2024 Honda Civic Hatchback Specifications & Features",
 "https://hondanews.com/en-US/honda-automobiles/releases/2024-honda-civic-hatchback-specifications-features",
 "American Honda Motor Co. (hondanews.com)","A",applicability="2024 Civic Hatchback, US market, all trims; 6MT column on Sport (2.0L) and Sport Touring (1.5T)",
 notes="Table columns LX/Sport/EX-L/Sport Touring checked in raw HTML; 6MT values in Sport and Sport Touring columns.",cache_file="cache/pages/2b1524caf89378a3.txt")
db.add_source(T,"tx:hondanews-us-2023-hatch-specs","2023 Honda Civic Hatchback Specifications & Features",
 "https://hondanews.com/en-US/honda-automobiles/releases/2023-honda-civic-hatchback-specifications-features",
 "American Honda Motor Co. (hondanews.com)","A",applicability="2023 Civic Hatchback, US",cache_file="cache/pages/ae42e10b45b3e86f.txt",
 notes="Used for model-year-change check.")
db.add_source(T,"tx:hondanews-us-2022-hatch-specs","2022 Honda Civic Hatchback Specifications & Features (Sept 20, 2021)",
 "https://hondanews.com/en-US/honda-automobiles/releases/release-cb177600e922c8a5fcfa01b9b80149e2-2022-honda-civic-hatchback-specifications-features",
 "American Honda Motor Co. (hondanews.com)","A",applicability="2022 Civic Hatchback, US",cache_file="cache/pages/fb1d5790fd3bfda8.txt",
 notes="Used for model-year-change check.")
db.add_source(T,"tx:hondainfocenter-us-2024-hatch-specs","2024 Civic Hatchback Specifications - Honda Information Center",
 "https://www.hondainfocenter.com/2024/Civic-Hatchback/Feature-Guide/Civic-Hatchback-Specifications/",
 "American Honda Motor Co. (Honda Information Center)","A",applicability="2024 Civic Hatchback, US",cache_file="cache/pages/b67f7f855816944e.txt",
 notes="data-model-identifier 2=Sport, 4=Sport Touring (checked in raw HTML). Prints trailing zeros dropped (2.08, 0.83, 4.1). Same publisher as hondanews.com, so not fully independent.")
db.add_source(T,"tx:hondanews-ca-2024-hatch-specs","2024 Honda Civic Hatchback Specifications (Honda Canada)",
 "https://hondanews.ca/en-CA/releases/release-1128768177ab00a73471b1938c152ddf-2024-honda-civic-hatchback-specifications",
 "Honda Canada Inc. (hondanews.ca)","A",applicability="2024 Civic Hatchback, Canada, Sport and Sport Touring",cache_file="cache/pages/22157798d6e48e1c.txt",
 notes="Lists 6MT as 'Available' on Sport Touring only; prints NO gear ratios.")

ST24US=db.app("2024","US","Sport Touring (and 2.0L Sport, same column values)","6MT",notes="US press spec table")
def us(year,sid):
    return db.app(year,"US","Sport Touring (and 2.0L Sport 6MT, same values)","6MT")
gears=[("gear_1","1st gear ratio","1st",3.643,"high"),("gear_2","2nd gear ratio","2nd",2.080,"high"),
 ("gear_3","3rd gear ratio","3rd",1.361,"high"),("gear_4","4th gear ratio","4th",1.024,"high"),
 ("gear_5","5th gear ratio","5th",0.830,"high"),("gear_6","6th gear ratio","6th",0.686,"high"),
 ("gear_reverse","Reverse gear ratio","Reverse",3.673,"low"),("final_drive","Final drive ratio","Final Drive",4.100,"critical")]
hic={"2nd":"2.08","5th":"0.83","Final Drive":"4.1"}
p22={"Final Drive":"4.10"}
for key,desc,label,val,imp in gears:
    k="transmission."+key
    s=f"{val:.3f}"
    db.add_candidate(T,k,desc,"1",imp,db.record(printed=(val,"ratio"),cls="A",source_id="tx:hondanews-us-2024-hatch-specs",
      locator="DRIVETRAIN > 6-Speed Manual Transmission (6MT) > Gear Ratios, row '%s', Sport Touring column"%label,
      evidence=f"6-Speed Manual Transmission (6MT) … Gear Ratios: … {label} - {s} - {s}",as_printed=s,
      applicability=us("2024",None),confidence="high",
      notes="US-market source. Honda Canada's 2024 spec sheet prints no ratios; no Canadian-specific ratio found. Unchanged 2022-2024 (see other candidates); 2.0L Sport 6MT column prints the same values. Si ratios/final drive differ and are excluded."))
    s3=hic.get(label,s)
    db.add_candidate(T,k,desc,"1",imp,db.record(printed=(float(s3),"ratio"),cls="A",source_id="tx:hondainfocenter-us-2024-hatch-specs",
      locator=f"Transmissions table, row '{label}', Sport Touring column (data-model-identifier 4)",
      evidence=f"6-Speed Manual Transmission (6MT) … {label} {s3} {s3}",as_printed=s3,applicability=us("2024",None),confidence="high",
      notes="Same publisher (American Honda) as hondanews.com; second Honda page, not fully independent. Trailing zeros dropped by the site."))
    db.add_candidate(T,k,desc,"1",imp,db.record(printed=(val,"ratio"),cls="A",source_id="tx:hondanews-us-2023-hatch-specs",
      locator=f"DRIVETRAIN > 6MT Gear Ratios, row '{label}'",evidence=f"Gear Ratios: … {label} - {s} - {s}",as_printed=s,
      applicability=us("2023",None),confidence="high",notes="Model-year check: identical to 2024."))
    s2=p22.get(label,s)
    db.add_candidate(T,k,desc,"1",imp,db.record(printed=(float(s2),"ratio"),cls="A",source_id="tx:hondanews-us-2022-hatch-specs",
      locator=f"TRANSMISSIONS > 6-Speed Manual Transmission (6MT), row '{label}'",evidence=f"6-Speed Manual Transmission (6MT) … {label} {s2} {s2}",as_printed=s2,
      applicability=us("2022",None),confidence="high",notes="Model-year check: identical to 2024."))
db.add_candidate(T,"transmission.availability_ca_2024","6MT availability, 2024 Canadian Civic Hatchback","text","medium",
  db.record(value="6MT available on Sport Touring only (Sport is CVT only)",unit="text",cls="A",source_id="tx:hondanews-ca-2024-hatch-specs",
  locator="DRIVETRAIN table, row '6-speed manual transmission (MT)'",evidence="6-speed manual transmission (MT) Available",as_printed="Available (Sport Touring column; Sport column blank)",
  applicability=db.app("2024","CA","Sport / Sport Touring","6MT"),confidence="high",notes="Column checked in raw HTML: ['6-speed manual transmission (MT)', '', 'Available']."))
db.add_candidate(T,"transmission.code","Manual gearbox designation / type code","text","low",
  db.unknown("text",searches=["hondanews.com/hondanews.ca 2022-2024 Civic Hatchback spec tables (no code printed)","hondapartsnow transmission listings (part numbers only)"],
  how_to_measure="Read the transmission identification label/stamp on the gearbox case (near the clutch housing), or a Honda service manual / EPC 'transmission assembly' entry."))
print(db.save(T))

D=db.load_or_new("drivetrain","Drivetrain"); D["sources"]={}; D["parameters"]={}
db.add_source(D,"dt:hondanews-ca-2022-hatch-debut","2022 Honda Civic Hatchback Makes Global Debut During Honda Civic Tour “Remix” Virtual Performance (June 23, 2021)",
 "https://hondanews.ca/en-CA/hci-automobiles/releases/release-f62a8a2e1d52802dd04a2618822ad44329120a90-2022-honda-civic-hatchback-makes-global-debut-during-honda-civic-tour-remix-virtual-performance",
 "Honda Canada Inc. (hondanews.ca)","A",applicability="2022 Civic Hatchback, Canada, all grades",cache_file="cache/pages/011b73eb9216ebcd.txt")
db.add_source(D,"dt:hondapartsnow-2024-civic-flywheel","2024 Honda Civic Flywheel (OEM parts listing)","https://www.hondapartsnow.com/oem-2024-honda-civic-flywheel.html",
 "HondaPartsNow (OEM parts retailer, Honda EPC data)","C",applicability="2024 Civic, by submodel",cache_file="cache/pages/1954cdd7ca9be057.txt")
db.add_source(D,"dt:hondapartsnow-2024-civic-differential","2024 Honda Civic Differential (OEM parts listing)","https://www.hondapartsnow.com/oem-2024-honda-civic-differential.html",
 "HondaPartsNow (OEM parts retailer, Honda EPC data)","C",applicability="2024 Civic, by submodel",cache_file="cache/pages/e97ba8fbe304ceb5.txt")
db.add_source(D,"dt:hondanews-ca-2024-hatch-specs","2024 Honda Civic Hatchback Specifications (Honda Canada)",
 "https://hondanews.ca/en-CA/releases/release-1128768177ab00a73471b1938c152ddf-2024-honda-civic-hatchback-specifications",
 "Honda Canada Inc. (hondanews.ca)","A",applicability="2024 Civic Hatchback, Canada",cache_file="cache/pages/22157798d6e48e1c.txt")
db.add_source(D,"dt:hondanews-us-2024-hatch-specs","2024 Honda Civic Hatchback Specifications & Features",
 "https://hondanews.com/en-US/honda-automobiles/releases/2024-honda-civic-hatchback-specifications-features","American Honda Motor Co.","A",
 applicability="2024 Civic Hatchback, US",cache_file="cache/pages/2b1524caf89378a3.txt")
CA22=db.app("2022","CA","all grades (LX, Sport, Sport Touring)","6MT",notes="2022 launch release; 6MT carried over unchanged 2022-2024 per identical US ratio tables")
db.add_candidate(D,"drivetrain.flywheel_type","Flywheel type","text","high",db.record(value="dual-mass",unit="text",cls="A",
  source_id="dt:hondanews-ca-2022-hatch-debut",locator="Powertrain section, paragraph beginning 'A new 6-speed manual transmission'",
  evidence="A new 6-speed manual transmission is available in all grades. The transmission has been revised for an even sportier feel with improved shift rigidity and shorter shift throws. A new dual-mass flywheel helps reduce noise and vibration transmitted through the drivetrain.",
  as_printed="dual-mass flywheel",applicability=CA22,confidence="high",
  notes="Contrast: the 11th-gen Si uses a single-mass flywheel (different part 22100-65P-003); not applicable here."))
db.add_candidate(D,"drivetrain.flywheel_part_number","OEM flywheel part number (1.5T Sport Touring 6MT)","text","low",db.record(value="22100-5CD-018 (replaces 22100-5CD-008)",unit="text",cls="C",
  source_id="dt:hondapartsnow-2024-civic-flywheel",locator="listing 'Part Number: 22100-5CD-018'",
  evidence="2024 Honda Civic Flywheel Part Number: 22100-5CD-018 … Replaces : 22100-5CD-008 … Fits the following 2024 Honda Civic Submodels: 5 Door 1.5T Sport Touring | 6MT",
  as_printed="22100-5CD-018",applicability=db.app("2024","US (EPC)","Sport Touring","6MT"),confidence="high",
  notes="Distinct from the Si (22100-65P-003), Type R (22100-65W-003) and 2.0L Sport 6MT (22100-65M-003) flywheels. MSRP $2458.10 vs $635.23 for the Si single-mass part is consistent with a dual-mass unit. Listed 'Item Weight: 34.60 Pounds' with box dimensions 15.5 x 15.2 x 6.1 in is a shipping weight, NOT a flywheel mass."))
db.add_candidate(D,"drivetrain.flywheel_shipping_weight","Listed item (shipping) weight of OEM flywheel 22100-5CD-018 — upper bound on flywheel mass only","kg","low",
  db.record(printed=(34.60,"lb"),cls="C",source_id="dt:hondapartsnow-2024-civic-flywheel",locator="22100-5CD-018 Product Specifications",
  evidence="Item Weight : 34.60 Pounds Item Dimensions : 15.5 x 15.2 x 6.1 inches",as_printed="34.60 Pounds",
  applicability=db.app("2024","US (EPC)","Sport Touring","6MT"),confidence="low",
  notes="Retailer shipping data (box dims listed); includes packaging. Use only as an upper bound for flywheel mass."))
db.add_candidate(D,"drivetrain.differential_type","Front differential type","text","critical",db.record(value="open (bevel-gear) differential; no mechanical LSD",unit="text",cls="C",
  source_id="dt:hondapartsnow-2024-civic-differential",locator="listing 'Part Number: 41100-57A-000'",
  evidence="2024 Honda Civic Differential Complete Part Number: 41100-57A-000 … Other Name Differential Case … Fits the following 2024 Honda Civic Submodels: 5 Door 1.5T Sport Touring, 5 Door 2.0L Sport | 6MT",
  as_printed="Differential Complete 41100-57A-000",applicability=db.app("2024","US (EPC)","Sport Touring (shared with 2.0L Sport)","6MT"),confidence="high",
  notes="Same listing shows the Si gets 'Differential Assembly, Helical Limited Slip' 41200-5CD-003 and the Type R 'LSD, ASSY- HELICAL' 41200-R3P-003; the Sport Touring 6MT part is not an LSD. No Honda spec sheet lists an LSD for the hatchback. Brake-based yaw control is separate: see drivetrain.agile_handling_assist."))
db.add_candidate(D,"drivetrain.agile_handling_assist","Agile Handling Assist (brake-based yaw-moment control) fitted","bool","medium",db.record(value=True,unit="bool",cls="A",
  source_id="dt:hondanews-ca-2024-hatch-specs",locator="CHASSIS table, row 'Agile Handling Assist2 (AHA)'",evidence="Agile Handling Assist2 (AHA) • •",as_printed="•",
  applicability=db.app("2024","CA","Sport and Sport Touring","CVT and 6MT"),confidence="high",
  notes="Listed as a chassis feature, not as a differential. AHA applies light individual-wheel braking to aid turn-in (yaw moment); Honda does not describe it as a limited-slip substitute and no evidence was found that it acts as a brake-based LSD on power. Do not model as an LSD."))
db.add_candidate(D,"drivetrain.hill_start_assist","Hill Start Assist fitted","bool","low",db.record(value=True,unit="bool",cls="A",
  source_id="dt:hondanews-ca-2024-hatch-specs",locator="CHASSIS table, row 'Hill Start Assist2'",evidence="Hill Start Assist2 • •",as_printed="•",
  applicability=db.app("2024","CA","Sport and Sport Touring","CVT and 6MT"),confidence="high",notes=""))
db.add_candidate(D,"drivetrain.idle_stop_mt","Auto idle-stop on the 6MT","bool","low",db.record(value=True,unit="bool",status="estimated",cls="E",
  source_id="dt:hondanews-ca-2024-hatch-specs",locator="ENGINE table, row 'Idle-stop'",evidence="Idle-stop • •",as_printed="•",range=[0,1],
  applicability=db.app("2024","CA","Sport and Sport Touring","CVT and 6MT (not split by gearbox)"),confidence="low",
  how_to_measure="Stop the real car in neutral with the clutch released, engine warm: note whether the engine shuts off and the idle-stop lamp lights; or read the owner's manual 'Auto Idle Stop' section for the MT.",
  notes="CONFLICTING EVIDENCE: 2024 Canadian and US spec tables mark Idle-stop for every trim column (the ST column includes the 6MT), but the 2022 Honda Canada launch release says 'a new standard idle-stop system (CVT only)' (dt:hondanews-ca-2022-hatch-debut, Powertrain paragraph on the 2.0L LX). Owner's manual not checked. Not decisive; treated as unknown-leaning-yes."))
db.add_candidate(D,"drivetrain.shift_mechanism","Shift mechanism description","text","low",db.record(value="cable-operated 6MT revised for shift rigidity and shorter throws",unit="text",cls="A",
  source_id="dt:hondanews-ca-2022-hatch-debut",locator="Powertrain section",evidence="The transmission has been revised for an even sportier feel with improved shift rigidity and shorter shift throws.",
  as_printed="improved shift rigidity and shorter shift throws",applicability=CA22,confidence="medium",notes="'cable-operated' is not stated by this source; hondapartsnow lists 'Shift Cable' among related 2024 Civic parts (lead only)."))
print(db.save(D))

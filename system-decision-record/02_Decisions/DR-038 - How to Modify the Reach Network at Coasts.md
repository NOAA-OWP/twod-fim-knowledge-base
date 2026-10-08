#terminal-reaches #network-modification
## Description
Define how the reach network is modified where it approaches coasts during the network modification phase. The goal is to stop modeling reach hydraulics near coasts where coastal models should provide FIMs.

## Alternatives

### ALT-A - Omit Reaches where Reach overlaps NOAA Tidal Surface Coverage
#current

1. Download NOAA tidal surface coverage (MHHW raster footprint)
   https://www.fisheries.noaa.gov/inport/item/48104
   https://coast.noaa.gov/slrdata/Tidal_Surfaces/index.html
2. Intersect reaches with the NOAA tidal surface extent
3. A reach fully within the coverage is dropped.
4. A reach only partially within (downstream end inside, upstream not) is trimmed to its upstream portion instead of dropped outright, and marked as a network break at the coast.
5. Any reach further downstream of a dropped or trimmed reach is also dropped. A network break at the coast shouldn't leave an orphaned fragment in the modeling network.

## Decision History
- 2026-05-28: Drafted from meeting with developers
- 2026-08-10: Added trim-vs-drop distinction (step 4) and downstream cascade drop (step 5) — the original 3-step version only covered the fully-encompassed case.

## Raw Dump for Future Consideration
Dylan Lee  [11:31 AM]

Hey [@Taher Chegini](https://nextgenwaterp-iod6272.slack.com/team/U09M3L3CMLN) and [@Lauren Schambach](https://nextgenwaterp-iod6272.slack.com/team/U08QD9YBUKS), [@Abdul Siddiqui](https://nextgenwaterp-iod6272.slack.com/team/U06FBTF83DX) has a question about the coastal boundaries around the hydrofabric. Would the inland boundaries of the SCHISM meshes be the best things to use here?



Taher Chegini  [11:33 AM]

Depends on the application, what's the use case?



Dylan Lee  [11:34 AM]

Not sure I'll let Abdul speak to that



Abdul Siddiqui  [11:37 AM]

Hey thanks for setting the thread.
We are looking for a dataset to use as a proxy for eliminating all reaches from NHF that we could reasonably assume would have tidal/coastal influence from our 2D modeling system. 2D modeling is expansive, so trying to limit the reaches we care about.

A little more details here and our current method.
[https://fictional-barnacle-437lwvo.pages.github.io/02_Decisions/DR-038---How-to-Modify-the-Reach-Network-at-Coasts](https://fictional-barnacle-437lwvo.pages.github.io/02_Decisions/DR-038---How-to-Modify-the-Reach-Network-at-Coasts)



[11:38 AM]

Let me know if link doesn't work for anyone.



Taher Chegini  [11:46 AM]

The link works, thanks! That's an active area of research that we actually proposed a methodology for to OWP. As a quick an dirty way, if you really need to do this some way, you can use the outline of SCHISM models that OWP has provided and then intersect with NHF divides to find the divides that OWP has marked as areas where coastal models should handle. The caveat is that the SCHISM meshes have known issues and limitations, so it's not a reliable source. [@Lauren Schambach](https://nextgenwaterp-iod6272.slack.com/team/U08QD9YBUKS) has worked on this more, so she can provide more details.



Abdul Siddiqui  [11:49 AM]

Thanks, this helps. We are looking for a quick and dirty way indeed. This is all R&D and prototype for foreseeable future.
Looking forward for details from [@Lauren Schambach](https://nextgenwaterp-iod6272.slack.com/team/U08QD9YBUKS).

What do you both think about the current methodology and associated dataset we have listed there.



Lauren Schambach  [11:50 AM]

Hey all - won't be able to check in on this until later today, will get back to you



Taher Chegini  [11:58 AM]

I think a missing component in the method that you linked is no discussion or consideration regarding inland-coastal handoff. Theoretically, we want the inland model to feed river discharges to a coastal model. So, I think a more NGEN consistent approach would be identify the flowpaths that are connected to the coastal model, then discarding all their downstream flowpaths.



Abdul Siddiqui  [12:01 PM]

That is exactly what we are after and you have laid it out in a good way.
Now we are looking for that dataset that delineate inland-coastal boundary. We are using MHHW as a proxy for that as a starter.

Dylan Lee  [12:02 PM]

We can do that identification of flowpaths at the SCHISM boundaries at least (edited) 



Abdul Siddiqui  [12:03 PM]

I haven't looked at that dataset, can you send me a link for that if you have it.



Taher Chegini  [12:04 PM]

Ah ok. Yes, in that case,, Dylan's suggestions, is the best we can do with the existing data.



Dylan Lee  [12:08 PM]

We would have to produce the flowpath/boundary intersections for all the SCHISM meshes. We have demoed it for the Atlantic mesh. [@Taher Chegini](https://nextgenwaterp-iod6272.slack.com/team/U09M3L3CMLN) do you remember where the meshes are located on S3?

The script that does the crosswalking is here: [https://github.com/NGWPC/icefabric/blob/main/tools/hydrofabric/create_coastal_crosswalk.py](https://github.com/NGWPC/icefabric/blob/main/tools/hydrofabric/create_coastal_crosswalk.py)



Taher Chegini  [12:12 PM]

All coastal data that OWP hs provided are on [s3://ngwpc-coastal/parm/](s3://ngwpc-coastal/parm/) (Data)



[12:15 PM]

I have developed a reader for SCHISM models here that includes a component for getting the boundary: [https://github.com/NGWPC/nwm-coastal/blob/development/src/coastal_calibration/schism/project_reader.py#L706](https://github.com/NGWPC/nwm-coastal/blob/development/src/coastal_calibration/schism/project_reader.py#L706)



Dylan Lee  [12:19 PM]

[@Abdul Siddiqui](https://nextgenwaterp-iod6272.slack.com/team/U06FBTF83DX) if you want to find all the flowpaths associated with those boundaries then the create_coastal_crosswalk script linked above only need a .gr3 mesh file (in the ngwpc-coastal/parm object) and a copy of nhf. I would use nhf 1.2.0 if you have issues with the script let me know since its only been tested on nhf 1.1.3



Abdul Siddiqui  [2:20 PM]

Okay, thanks. I will probably ask one of our devs to have a look at it.
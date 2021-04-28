import ROOT
import os
import numpy as np

ROOT.gSystem.Load(os.environ['WCSIMDIR'] + "/libWCSimRoot.so")

class WCSim:
    def __init__(self, tree):
        print("number of entries in the geometry tree: " +
              str(self.geotree.GetEntries()))
        self.geotree.GetEntry(0)
        self.geo = self.geotree.wcsimrootgeom
        self.num_pmts = self.geo.GetWCNumPMT()
        self.tree = tree
        self.nevent = self.tree.GetEntries()
        print("number of entries in the tree: " + str(self.nevent))
        # Get first event and trigger to prevent segfault when later deleting
        # trigger to prevent memory leak
        self.tree.GetEvent(0)
        self.current_event = 0
        # 20" PMT trigger info
        self.event_20 = self.tree.wcsimrootevent
        self.ntrigger_20 = self.event_20.GetNumberOfEvents()
        self.trigger_20 = self.event_20.GetTrigger(0)
        self.current_trigger_20 = 0
        # 3" PMT trigger info
        # The trigger for 20" and 3" PMTs are separate
        self.event_3 = self.tree.wcsimrootevent2
        self.ntrigger_3 = self.event_3.GetNumberOfEvents()
        self.trigger_3 = self.event_3.GetTrigger(0)
        self.current_trigger_3 = 0

    def get_event(self, ev):
        # Delete previous triggers to prevent memory leak (only if file does
        # not change)
        # FIXME! don't quite know how it's called, might need future adjustment
        triggers_20 = [self.event_20.GetTrigger(i) for i in range(self.ntrigger_20)]
        triggers_3 = [self.event_3.GetTrigger(i) for i in range(self.ntrigger_3)]
        oldfile = self.tree.GetCurrentFile()
        self.tree.GetEvent(ev)
        if self.tree.GetCurrentFile() == oldfile:
            [t.Delete() for t in triggers_20]
            [t.Delete() for t in triggers_3]
        self.current_event = ev
        self.event_20 = self.tree.wcsimrootevent
        self.event_3 = self.tree.wcsimrootevent2
        self.ntrigger_20 = self.event_20.GetNumberOfEvents()
        self.ntrigger_3 = self.event_3.GetNumberOfEvents()

    # Chose to create two sets of every method that differs for two PMT types
    # instead of one method but modifying the variable names

    def get_trigger_20(self, trig):
        self.trigger_20 = self.event_20.GetTrigger(trig)
        self.current_trigger_20 = trig
        return self.trigger_20

    def get_trigger_3(self, trig):
        self.trigger_3 = self.event_3.GetTrigger(trig)
        self.current_trigger_3 = trig
        return self.trigger_3

    def get_first_trigger_20(self):
        first_trigger = 0
        first_trigger_time = 9999999.0
        for index in range(self.ntrigger_20):
            self.get_trigger_20(index)
            trigger_time = self.trigger_20.GetHeader().GetDate() # this trigger_20 might be a problem,
                                                                 # where is trigger time getting this from?
            if trigger_time < first_trigger_time:
                first_trigger_time = trigger_time
                first_trigger = index
        return self.get_trigger_20(first_trigger)

    def get_first_trigger_3(self):
        first_trigger = 0
        first_trigger_time = 9999999.0
        for index in range(self.ntrigger_3):
            self.get_trigger_3(index)
            trigger_time = self.trigger_3.GetHeader().GetDate() # this trigger_3 might be a problem,
                                                                # where is trigger time getting this from?
            if trigger_time < first_trigger_time:
                first_trigger_time = trigger_time
                first_trigger = index
        return self.get_trigger_3(first_trigger)

    def get_truth_info(self):
        # deprecated: should now use get_event_info instead, leaving here for 
        # use with old files
        # Since it's not in use, just added "_20" to keep the consistency but
        # not introducing it for "_3"
        self.get_trigger_20(0)
        tracks = self.trigger_20.GetTracks()
        energy = []
        position = []
        direction = []
        pid = []
        for i in range(self.trigger_20.GetNtrack()):
            if tracks[i].GetParenttype() == 0 and tracks[i].GetFlag() == 0\
                    and tracks[i].GetIpnu() in [22, 11, -11, 13, -13, 111]:
                pid.append(tracks[i].GetIpnu())
                position.append([tracks[i].GetStart(0), tracks[i].GetStart(1), tracks[i].GetStart(2)])
                direction.append([tracks[i].GetDir(0), tracks[i].GetDir(1), tracks[i].GetDir(2)])
                energy.append(tracks[i].GetE())
        return direction, energy, pid, position

    def get_event_info_20(self):
        # Depending on if the primary particle info can be accessed through 
        # both 20" and 3", the "_20" might be dropped FIXME!!
        self.get_trigger_20(0)
        tracks = self.trigger_20.GetTracks()
        # Primary particles with no parent are the initial simulation
        particles = [t for t in tracks if t.GetFlag() == 0 and t.GetParenttype() == 0]
        # Check there is exactly one particle with no parent:
        if len(particles) == 1:
            # Only one primary, this is the particle being simulated
            return {
                "pid": particles[0].GetIpnu(),
                "position": [particles[0].GetStart(i) for i in range(3)],
                "direction": [particles[0].GetDir(i) for i in range(3)],
                "energy": particles[0].GetE()
            }
        # Particle with flag -1 is the incoming neutrino or 'dummy neutrino' 
        # used for gamma WCSim saves the gamma details (except position) in 
        # the neutrino track with flag -1
        neutrino = [t for t in tracks if t.GetFlag() == -1]
        # Check for dummy neutrino that actually stores a gamma that converts to e+ / e-
        isConversion = len(particles) == 2 and {p.GetIpnu() for p in particles} == {11, -11}
        if isConversion and len(neutrino) == 1 and neutrino[0].GetIpnu() == 22:
            return {
                "pid": 22,
                "position": [particles[0].GetStart(i) for i in range(3)], # e+ / e- should have same position
                "direction": [neutrino[0].GetDir(i) for i in range(3)],
                "energy": neutrino[0].GetE()
            }
        # Check for dummy neutrino from old gamma simulations that didn't save
        # the gamma info
        if isConversion and len(neutrino) == 1 and neutrino[0].GetIpnu() == 12 \
                        and neutrino[0].GetE() < 0.0001:
            # Should be a positron/electron pair from a gamma simulation 
            # (temporary hack since no gamma truth saved)
            momentum = [sum(p.GetDir(i) * p.GetP() for p in particles) for i in range(3)]
            norm = np.sqrt(sum(p ** 2 for p in momentum))
            return {
                "pid": 22,
                "position": [particles[0].GetStart(i) for i in range(3)],  # e+ / e- should have same position
                "direction": [p / norm for p in momentum],
                "energy": sum(p.GetE() for p in particles)
            }
        # Otherwise something else is going on... guess info from the primaries
        momentum = [sum(p.GetDir(i) * p.GetP() for p in particles) for i in range(3)]
        norm = np.sqrt(sum(p ** 2 for p in momentum))
        return {
            "pid": 0,  # there's more than one particle so just use pid 0
            "position": [sum(p.GetStart(i) for p in particles)/len(particles) for i in range(3)],  # average position
            "direction": [p / norm for p in momentum],  # direction of sum of momenta
            "energy": sum(p.GetE() for p in particles)  # sum of energies
        }

    def get_digitized_hits_20(self):
        position_20 = []
        charge_20 = []
        time_20 = []
        pmt_20 = []
        trigger_20 = []
        for t in range(self.ntrigger_20):
            self.get_trigger_20(t)
            for hit in self.trigger_20.GetCherenkovDigiHits():
                pmt_id = hit.GetTubeId() - 1
                position_20.append([self.geo.GetPMT(pmt_id, 0).GetPosition(j)
                                   for j in range(3)])
                charge_20.append(hit.GetQ())
                time_20.append(hit.GetT())
                pmt_20.append(pmt_id)
                trigger_20.append(t)
        hits = {
            "position_20": np.asarray(position_20, dtype=np.float32),
            "charge_20": np.asarray(charge_20, dtype=np.float32),
            "time_20": np.asarray(time_20, dtype=np.float32),
            "pmt_20": np.asarray(pmt_20, dtype=np.int32),
            "trigger_20": np.asarray(trigger_20, dtype=np.int32)
        }
        return hits

    def get_digitized_hits_3(self):
        position_3 = []
        charge_3 = []
        time_3 = []
        pmt_3 = []
        trigger_3 = []
        for t in range(self.ntrigger_3):
            self.get_trigger_3(t)
            for hit in self.trigger_3.GetCherenkovDigiHits():
                pmt_id = hit.GetmPMT_PMTId() - 1 # Don't know if I need to minus
                                                 # 1 for mPMTs as well FIXME
                position_3.append([self.geo.GetPMT(pmt_id, 1).GetPosition(j)
                                   for j in range(3)])
                charge_3.append(hit.GetQ())
                time_3.append(hit.GetT())
                pmt_3.append(pmt_id)
                trigger_3.append(t)
        hits = {
            "position_3": np.asarray(position_3, dtype=np.float32),
            "charge_3": np.asarray(charge_3, dtype=np.float32),
            "time_3": np.asarray(time_3, dtype=np.float32),
            "pmt_3": np.asarray(pmt_3, dtype=np.int32),
            "trigger_3": np.asarray(trigger_3, dtype=np.int32)
        }
        return hits

    def get_true_hits_20(self):
        position_20 = []
        track_20 = []
        pmt_20 = []
        PE_20 = []
        trigger_20 = []
        for t in range(self.ntrigger_20):
            self.get_trigger_20(t)
            for hit in self.trigger_20.GetCherenkovHits():
                pmt_id = hit.GetTubeID() - 1
                tracks_20 = set()
                for j in range(hit.GetTotalPe(0), hit.GetTotalPe(0)+hit.GetTotalPe(1)):
                    pe = self.trigger_20.GetCherenkovHitTimes().At(j)
                    tracks_20.add(pe.GetParentID())
                position_20.append([self.geo.GetPMT(pmt_id, 0).GetPosition(k) 
                                    for k in range(3)])
                track_20.append(tracks_20.pop() if len(tracks_20) == 1 else -2)
                pmt_20.append(pmt_id)
                PE_20.append(hit.GetTotalPe(1))
                trigger_20.append(t)
        hits = {
            "position_20": np.asarray(position_20, dtype=np.float32),
            "track_20": np.asarray(track_20, dtype=np.int32),
            "pmt_20": np.asarray(pmt_20, dtype=np.int32),
            "PE_20": np.asarray(PE_20, dtype=np.int32),
            "trigger_20": np.asarray(trigger_20, dtype=np.int32)
        }
        return hits

    def get_true_hits_3(self):
        position_3 = []
        track_3 = []
        pmt_3 = []
        PE_3 = []
        trigger_3 = []
        for t in range(self.ntrigger_3):
            self.get_trigger_3(t)
            for hit in self.trigger_3.GetCherenkovHits():
                pmt_id = hit.GetmPMT_PMTId() - 1
                tracks_3 = set()
                for j in range(hit.GetTotalPe(0), hit.GetTotalPe(0)+hit.GetTotalPe(1)):
                    pe = self.trigger_3.GetCherenkovHitTimes().At(j)
                    tracks_3.add(pe.GetParentID())
                position_3.append([self.geo.GetPMT(pmt_id, 1).GetPosition(k) 
                                    for k in range(3)])
                track_3.append(tracks_3.pop() if len(tracks_3) == 1 else -2)
                pmt_3.append(pmt_id)
                PE_3.append(hit.GetTotalPe(1))
                trigger_3.append(t)
        hits = {
            "position_3": np.asarray(position_3, dtype=np.float32),
            "track_3": np.asarray(track_3, dtype=np.int32),
            "pmt_3": np.asarray(pmt_3, dtype=np.int32),
            "PE_3": np.asarray(PE_3, dtype=np.int32),
            "trigger_3": np.asarray(trigger_3, dtype=np.int32)
        }
        return hits

    def get_hit_photons_20(self):
        start_position_20 = []
        end_position_20 = []
        start_time_20 = []
        end_time_20 = []
        track_20 = []
        pmt_20 = []
        trigger_20 = []
        for t in range(self.ntrigger_20):
            self.get_trigger_20(t)
            n_photons = self.trigger_20.GetNcherenkovhittimes()
            trigger_20.append(np.full(n_photons, t, dtype=np.int32))
            counts = [h.GetTotalPe(1) for h in self.trigger_20.GetCherenkovHits()]
            hit_pmts = [h.GetTubeID()-1 for h in self.trigger_20.GetCherenkovHits()]
            pmt_20.append(np.repeat(hit_pmts, counts))
            end_time_20.append(np.zeros(n_photons, dtype=np.float32))
            track_20.append(np.zeros(n_photons, dtype=np.int32))
            start_time_20.append(np.zeros(n_photons, dtype=np.float32))
            start_position_20.append(np.zeros((n_photons, 3), dtype=np.float32))
            end_position_20.append(np.zeros((n_photons, 3), dtype=np.float32))
            photons = self.trigger_20.GetCherenkovHitTimes()
            end_time[t][:] = [p.GetTruetime() for p in photons]
            track[t][:] = [p.GetParentID() for p in photons]
            try:  # Only works with new tracking branch of WCSim
                start_time[t][:] = [p.GetPhotonStartTime() for p in photons]
                for i in range(3):
                    start_position[t][:,i] = [p.GetPhotonStartPos(i)/10 for p in photons]
                    end_position[t][:,i] = [p.GetPhotonEndPos(i)/10 for p in photons]
            except AttributeError: # leave as zeros if not using tracking branch
                pass
        photons = {
            "start_position_20": np.concatenate(start_position_20),
            "end_position_20": np.concatenate(end_position_20),
            "start_time_20": np.concatenate(start_time_20),
            "end_time_20": np.concatenate(end_time_20),
            "track_20": np.concatenate(track_20),
            "pmt_20": np.concatenate(pmt_20),
            "trigger_20": np.concatenate(trigger_20)
        }
        return photons

    def get_hit_photons_3(self):
        start_position_3 = []
        end_position_3 = []
        start_time_3 = []
        end_time_3 = []
        track_3 = []
        pmt_3 = []
        trigger_3 = []
        for t in range(self.ntrigger_3):
            self.get_trigger_3(t)
            n_photons = self.trigger_3.GetNcherenkovhittimes()
            trigger_3.append(np.full(n_photons, t, dtype=np.int32))
            counts = [h.GetTotalPe(1) for h in self.trigger_3.GetCherenkovHits()]
            hit_pmts = [h.GetmPMT_PMTID()-1 for h in self.trigger_3.GetCherenkovHits()]
            pmt_3.append(np.repeat(hit_pmts, counts))
            end_time_3.append(np.zeros(n_photons, dtype=np.float32))
            track_3.append(np.zeros(n_photons, dtype=np.int32))
            start_time_3.append(np.zeros(n_photons, dtype=np.float32))
            start_position_3.append(np.zeros((n_photons, 3), dtype=np.float32))
            end_position_3.append(np.zeros((n_photons, 3), dtype=np.float32))
            photons = self.trigger_3.GetCherenkovHitTimes()
            end_time[t][:] = [p.GetTruetime() for p in photons]
            track[t][:] = [p.GetParentID() for p in photons]
            try:  # Only works with new tracking branch of WCSim
                start_time[t][:] = [p.GetPhotonStartTime() for p in photons]
                for i in range(3):
                    start_position[t][:,i] = [p.GetPhotonStartPos(i)/10 for p in photons]
                    end_position[t][:,i] = [p.GetPhotonEndPos(i)/10 for p in photons]
            except AttributeError: # leave as zeros if not using tracking branch
                pass
        photons = {
            "start_position_3": np.concatenate(start_position_3),
            "end_position_3": np.concatenate(end_position_3),
            "start_time_3": np.concatenate(start_time_3),
            "end_time_3": np.concatenate(end_time_3),
            "track_3": np.concatenate(track_3),
            "pmt_3": np.concatenate(pmt_3),
            "trigger_3": np.concatenate(trigger_3)
        }
        return photons


    def get_tracks(self):
        track_id = []
        pid = []
        start_time = []
        energy = []
        start_position = []
        stop_position = []
        parent = []
        flag = []
        for t in range(self.ntrigger_20):
            self.get_trigger_20(t)
            for track in self.trigger_20.GetTracks():
                track_id.append(track.GetId())
                pid.append(track.GetIpnu())
                start_time.append(track.GetTime())
                energy.append(track.GetE())
                start_position.append([track.GetStart(i) for i in range(3)])
                stop_position.append([track.GetStop(i) for i in range(3)])
                parent.append(track.GetParenttype())
                flag.append(track.GetFlag())
        tracks = {
            "id": np.asarray(track_id, dtype=np.int32),
            "pid": np.asarray(pid, dtype=np.int32),
            "start_time": np.asarray(start_time, dtype=np.float32),
            "energy": np.asarray(energy, dtype=np.float32),
            "start_position": np.asarray(start_position, dtype=np.float32),
            "stop_position": np.asarray(stop_position, dtype=np.float32),
            "parent": np.asarray(parent, dtype=np.int32),
            "flag": np.asarray(flag, dtype=np.int32)
        }
        return tracks

    def get_triggers_20(self):
        trigger_times_20 = np.empty(self.ntrigger_20, dtype=np.float32)
        trigger_types_20 = np.empty(self.ntrigger_20, dtype=np.int32)
        for t in range(self.ntrigger_20):
            self.get_trigger_20(t)
            trigger_times_20[t] = self.trigger_20.GetHeader().GetDate()
            trig_type = self.trigger_20.GetTriggerType()
            if trig_type > np.iinfo(np.int32).max:
                trig_type = -1
            trigger_types_20[t] = trig_type
        triggers = {
                "time_20": trigger_times_20,
                "type_20": trigger_types_20
        }
        return triggers

    def get_triggers_3(self):
        trigger_times_3 = np.empty(self.ntrigger_3, dtype=np.float32)
        trigger_types_3 = np.empty(self.ntrigger_3, dtype=np.int32)
        for t in range(self.ntrigger_3):
            self.get_trigger_3(t)
            trigger_times_3[t] = self.trigger_3.GetHeader().GetDate()
            trig_type = self.trigger_3.GetTriggerType()
            if trig_type > np.iinfo(np.int32).max:
                trig_type = -1
            trigger_types_3[t] = trig_type
        triggers = {
                "time_3": trigger_times_3,
                "type_3": trigger_types_3
        }
        return triggers


class WCSimFile(WCSim):
    def __init__(self, filename):
        self.file = ROOT.TFile(filename, "read")
        tree = self.file.Get("wcsimT")
        self.geotree = self.file.Get("wcsimGeoT")
        super().__init__(tree)

    def __del__(self):
        self.file.Close()


class WCSimChain(WCSim):
    def __init__(self, filenames):
        self.chain = ROOT.TChain("wcsimT")
        for file in filenames:
            self.chain.Add(file)
        self.file = self.GetFile()
        self.geotree = self.file.Get("wcsimGeoT")
        super().__init__(self.chain)

def get_label(infile):
    if "_gamma" in infile:
        label = 0
    elif "_e" in infile:
        label = 1
    elif "_mu" in infile:
        label = 2
    elif "_pi0" in infile:
        label = 3
    else:
        print("Unknown input file particle type")
        raise SystemExit
    return label

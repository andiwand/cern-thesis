#ifndef MyEventAction_h
#define MyEventAction_h 1

#include "MyRunAction.hpp"

#include "G4Event.hh"
#include "G4RunManager.hh"
#include "G4UserEventAction.hh"
#include "globals.hh"

class MyEventAction : public G4UserEventAction {
public:
  MyEventAction() {}

  ~MyEventAction() override = default;

  void BeginOfEventAction(const G4Event *event) override {}

  void EndOfEventAction(const G4Event *event) override {
    // get number of stored trajectories

    G4TrajectoryContainer *trajectoryContainer =
        event->GetTrajectoryContainer();
    G4int n_trajectories = 0;
    if (trajectoryContainer)
      n_trajectories = trajectoryContainer->entries();

    // periodic printing

    G4int eventID = event->GetEventID();
    if (eventID < 100 || eventID % 100 == 0) {
      G4cout << ">>> Event: " << eventID << G4endl;
      if (trajectoryContainer) {
        G4cout << "    " << n_trajectories
               << " trajectories stored in this event." << G4endl;
      }
      G4VHitsCollection *hc = event->GetHCofThisEvent()->GetHC(0);
      G4cout << "    " << hc->GetSize() << " hits stored in this event"
             << G4endl;
    }
  }

private:
};

#endif

#pragma once

#include "G4RunManager.hh"
#include "G4Step.hh"
#include "G4UserSteppingAction.hh"

class MySteppingAction : public G4UserSteppingAction {
public:
  explicit MySteppingAction(bool kill_secondaries)
      : m_kill_secondaries(kill_secondaries) {}

  void UserSteppingAction(const G4Step *step) override {
    G4StepPoint *prePoint = step->GetPreStepPoint();
    G4StepPoint *postPoint = step->GetPostStepPoint();

    G4String procName = postPoint->GetProcessDefinedStep()->GetProcessName();
    // std::cout << procName << std::endl;

    if (m_kill_secondaries && step->GetTrack()->GetParentID() != 0) {
      step->GetTrack()->SetTrackStatus(G4TrackStatus::fStopAndKill);
    }
  }

private:
  bool m_kill_secondaries;
};

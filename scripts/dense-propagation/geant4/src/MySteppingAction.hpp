#ifndef MySteppingAction_h
#define MySteppingAction_h 1

#include "G4Event.hh"
#include "G4LogicalVolume.hh"
#include "G4RunManager.hh"
#include "G4Step.hh"
#include "G4UserSteppingAction.hh"
#include "globals.hh"

class MySteppingAction : public G4UserSteppingAction {
public:
  MySteppingAction() {}

  ~MySteppingAction() override = default;

  void UserSteppingAction(const G4Step *step) override {
    G4StepPoint *prePoint = step->GetPreStepPoint();
    G4StepPoint *postPoint = step->GetPostStepPoint();

    G4String procName = postPoint->GetProcessDefinedStep()->GetProcessName();
    //std::cout << procName << std::endl;
  }

private:
};

#endif

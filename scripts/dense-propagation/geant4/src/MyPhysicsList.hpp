#ifndef MyPhysicsList_h
#define MyPhysicsList_h 1

#include "G4DecayPhysics.hh"
#include "G4EmStandardPhysics.hh"
#include "G4RadioactiveDecayPhysics.hh"
#include "G4VModularPhysicsList.hh"

class MyPhysicsList : public G4VModularPhysicsList {
public:
  MyPhysicsList() {
    SetVerboseLevel(1);

    // Default physics
    RegisterPhysics(new G4DecayPhysics());

    // EM physics
    RegisterPhysics(new G4EmStandardPhysics());

    // Radioactive decay
    RegisterPhysics(new G4RadioactiveDecayPhysics());
  }

  ~MyPhysicsList() override = default;

  void SetCuts() override { G4VUserPhysicsList::SetCuts(); }
};

#endif

#ifndef MyPrimaryGeneratorAction_h
#define MyPrimaryGeneratorAction_h 1

#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4LogicalVolumeStore.hh"
#include "G4ParticleDefinition.hh"
#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4RunManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4VUserPrimaryGeneratorAction.hh"
#include "Randomize.hh"
#include "globals.hh"

class MyPrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction {
public:
  MyPrimaryGeneratorAction() {
    G4int n_particle = 1;
    fParticleGun = new G4ParticleGun(n_particle);

    // default particle kinematic
    G4ParticleTable *particleTable = G4ParticleTable::GetParticleTable();
    G4String particleName = "mu+";
    G4ParticleDefinition *particle = particleTable->FindParticle(particleName);
    fParticleGun->SetParticleDefinition(particle);
    fParticleGun->SetParticlePosition(G4ThreeVector(-1.5 * CLHEP::m, 0, 0));
    fParticleGun->SetParticleMomentumDirection(G4ThreeVector(1., 0., 0.));
    fParticleGun->SetParticleEnergy(1. * CLHEP::GeV);
  }

  ~MyPrimaryGeneratorAction() override { delete fParticleGun; }

  // method from the base class
  void GeneratePrimaries(G4Event *anEvent) override {
    // this function is called at the begining of ecah event
    //

    // In order to avoid dependence of PrimaryGeneratorAction
    // on DetectorConstruction class we get Envelope volume
    // from G4LogicalVolumeStore.

    fParticleGun->GeneratePrimaryVertex(anEvent);
  }

  // method to access particle gun
  const G4ParticleGun *GetParticleGun() const { return fParticleGun; }

private:
  G4ParticleGun *fParticleGun = nullptr; // pointer a to G4 gun class
  G4Box *fWorldBox = nullptr;
};

#endif

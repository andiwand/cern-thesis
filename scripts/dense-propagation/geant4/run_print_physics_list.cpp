#include "MyDetectorConstruction.hpp"
#include "MyLogActionInitialization.hpp"

#include "FTFP_BERT.hh"
#include "FTFP_BERT_ATL.hh"
#include "G4RunManagerFactory.hh"
#include "G4StepLimiterPhysics.hh"
#include "G4SteppingVerbose.hh"
#include "G4UIExecutive.hh"
#include "G4UImanager.hh"
#include "G4VisExecutive.hh"
#include "Randomize.hh"

int main(int argc, char **argv) {
  // Optionally: choose a different Random engine...
  // G4Random::setTheEngine(new CLHEP::MTwistEngine);

  // use G4SteppingVerboseWithUnits
  G4int precision = 4;
  G4SteppingVerbose::UseBestUnit(precision);

  // Construct the default run manager
  //
  auto *runManager =
      G4RunManagerFactory::CreateRunManager(G4RunManagerType::Serial);

  // Set mandatory initialization classes
  //
  // Detector construction
  runManager->SetUserInitialization(
      new MyDetectorConstruction("G4_Fe", 1 * mm));

  // Physics list
  G4VModularPhysicsList *physicsList = new FTFP_BERT();

  G4StepLimiterPhysics *stepLimitPhys = new G4StepLimiterPhysics();
  physicsList->RegisterPhysics(stepLimitPhys);

  runManager->SetUserInitialization(physicsList);

  // User action initialization
  runManager->SetUserInitialization(new MyLogActionInitialization());

  runManager->Initialize();
  runManager->BeamOn(0);

  // Job termination
  // Free the store: user actions, physics_list and detector_description are
  // owned and deleted by the run manager, so they should not be deleted
  // in the main() program !
  delete runManager;
}

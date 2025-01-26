#include "MyActionInitialization.hpp"
#include "MyDetectorConstruction.hpp"

#include "FTFP_BERT.hh"
#include "G4RunManagerFactory.hh"
#include "G4StepLimiterPhysics.hh"
#include "G4SteppingVerbose.hh"
#include "G4UImanager.hh"

#include <iostream>

int main(int argc, char **argv) {
  if (argc != 2) {
    std::cerr << "Usage: " << argv[0] << " energy" << std::endl;
    return 1;
  }

  std::string energy = argv[1];

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
      new MyDetectorConstruction("G4_lAr", 1 * m));

  // Physics list
  G4VModularPhysicsList *physicsList = new FTFP_BERT();

  G4StepLimiterPhysics *stepLimitPhys = new G4StepLimiterPhysics();
  physicsList->RegisterPhysics(stepLimitPhys);

  runManager->SetUserInitialization(physicsList);

  // User action initialization
  runManager->SetUserInitialization(new MyActionInitialization());

  G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

  analysisManager->OpenFile("chart_eloss.root");

  // runManager->SetVerboseLevel(2);
  // analysisManager->SetVerboseLevel(1);
  // G4EventManager::GetEventManager()->SetVerboseLevel(2);
  // G4EventManager::GetEventManager()->GetTrackingManager()->SetVerboseLevel(2);
  // G4EventManager::GetEventManager()->GetStackManager()->SetVerboseLevel(2);

  runManager->Initialize();

  G4UImanager *uiManager = G4UImanager::GetUIpointer();
  uiManager->ApplyCommand(("/gun/energy " + energy).c_str());

  runManager->BeamOn(10000);

  analysisManager->Write();
  analysisManager->CloseFile();

  // Job termination
  // Free the store: user actions, physics_list and detector_description are
  // owned and deleted by the run manager, so they should not be deleted
  // in the main() program !
  delete runManager;
}

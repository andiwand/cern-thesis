#include "MyActionInitialization.hpp"
#include "MyDetectorConstruction.hpp"

#include "FTFP_BERT.hh"
#include "G4RunManagerFactory.hh"
#include "G4SteppingVerbose.hh"
#include "G4UImanager.hh"

#include <iostream>
#include <string>

int main(int argc, char **argv) {
  if (argc != 6) {
    std::cerr << "Usage: " << argv[0]
              << " threads energy material thickness output" << std::endl;
    std::cerr << "Example: " << argv[0] << " 1 1 G4_lAr 1000 output.root"
              << std::endl;
    return 1;
  }

  int threads = std::stoi(argv[1]);
  double energy = std::stod(argv[2]);
  std::string material = argv[3];
  double thickness = std::stod(argv[4]);
  std::string output = argv[5];

  if (material == "lar") {
    material = "G4_lAr";
  } else if (material == "fe") {
    material = "G4_Fe";
  }

  // use G4SteppingVerboseWithUnits
  G4int precision = 4;
  G4SteppingVerbose::UseBestUnit(precision);

  // Construct the default run manager
  //
  auto *runManager = G4RunManagerFactory::CreateRunManager(
      threads <= 1 ? G4RunManagerType::Serial : G4RunManagerType::MT, threads);

  // Set mandatory initialization classes
  //
  // Detector construction
  runManager->SetUserInitialization(
      new MyDetectorConstruction(material, thickness * mm));

  // Physics list
  G4VModularPhysicsList *physicsList = new FTFP_BERT();

  // G4StepLimiterPhysics *stepLimitPhys = new G4StepLimiterPhysics();
  // physicsList->RegisterPhysics(stepLimitPhys);

  runManager->SetUserInitialization(physicsList);

  // User action initialization
  runManager->SetUserInitialization(new MyActionInitialization(output));

  // runManager->SetVerboseLevel(2);
  // analysisManager->SetVerboseLevel(1);
  // G4EventManager::GetEventManager()->SetVerboseLevel(2);
  // G4EventManager::GetEventManager()->GetTrackingManager()->SetVerboseLevel(2);
  // G4EventManager::GetEventManager()->GetStackManager()->SetVerboseLevel(2);

  runManager->Initialize();

  G4UImanager *uiManager = G4UImanager::GetUIpointer();
  uiManager->ApplyCommand(
      ("/gun/energy " + std::to_string(static_cast<int>(energy)) + " GeV")
          .c_str());

  // inactivate to disable the process
  uiManager->ApplyCommand("/process/activate muIoni");
  uiManager->ApplyCommand("/process/activate muBrems");
  uiManager->ApplyCommand("/process/activate muPairProd");
  uiManager->ApplyCommand("/process/activate muonNuclear");

  runManager->BeamOn(10000);

  // Job termination
  // Free the store: user actions, physics_list and detector_description are
  // owned and deleted by the run manager, so they should not be deleted
  // in the main() program !
  delete runManager;
}

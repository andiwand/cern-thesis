#include "MyDetectorConstruction.hpp"
#include "MyLogActionInitialization.hpp"

#include "FTFP_BERT.hh"
#include "G4RunManagerFactory.hh"
#include "G4SteppingVerbose.hh"
#include "G4UImanager.hh"

int main(int argc, char **argv) {
  if (argc != 5) {
    std::cerr << "Usage: " << argv[0] << " threads material thickness output"
              << std::endl;
    std::cerr << "Example: " << argv[0] << " 1 G4_lAr 1000 output.root"
              << std::endl;
    return 1;
  }

  int threads = std::stoi(argv[1]);
  std::string material = argv[2];
  double thickness = std::stod(argv[3]);
  std::string output = argv[4];

  if (material == "lar") {
    material = "G4_lAr";
  } else if (material == "fe") {
    material = "G4_Fe";
  }
  G4NistManager *nist = G4NistManager::Instance();
  G4Material *mat = nist->FindOrBuildMaterial(material.c_str());
  if (mat == nullptr) {
    std::cerr << "Material " << material << " not found" << std::endl;
    return 1;
  }

  // Optionally: choose a different Random engine...
  // G4Random::setTheEngine(new CLHEP::MTwistEngine);

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
      new MyDetectorConstruction(material.c_str(), thickness * mm));

  // Physics list
  G4VModularPhysicsList *physicsList = new FTFP_BERT();

  // G4StepLimiterPhysics *stepLimitPhys = new G4StepLimiterPhysics();
  // physicsList->RegisterPhysics(stepLimitPhys);

  runManager->SetUserInitialization(physicsList);

  // User action initialization
  runManager->SetUserInitialization(new MyLogActionInitialization(output));

  // runManager->SetVerboseLevel(2);
  // analysisManager->SetVerboseLevel(1);
  // G4EventManager::GetEventManager()->SetVerboseLevel(2);
  // G4EventManager::GetEventManager()->GetTrackingManager()->SetVerboseLevel(2);
  // G4EventManager::GetEventManager()->GetStackManager()->SetVerboseLevel(2);

  runManager->Initialize();

  G4UImanager *uiManager = G4UImanager::GetUIpointer();
  // inactivate to disable the process
  uiManager->ApplyCommand("/process/activate muIoni");
  uiManager->ApplyCommand("/process/activate muBrems");
  uiManager->ApplyCommand("/process/activate muPairProd");
  uiManager->ApplyCommand("/process/activate muonNuclear");

  runManager->BeamOn(1000000);

  // Job termination
  // Free the store: user actions, physics_list and detector_description are
  // owned and deleted by the run manager, so they should not be deleted
  // in the main() program !

  delete runManager;
}

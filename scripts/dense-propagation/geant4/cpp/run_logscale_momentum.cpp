#include "MyDetectorConstruction.hpp"
#include "MyLogActionInitialization.hpp"

#include "FTFP_BERT.hh"
#include "G4RunManagerFactory.hh"
#include "G4SteppingVerbose.hh"
#include "G4UImanager.hh"

int main(int argc, char **argv) {
  if (argc != 3) {
    std::cerr << "Usage: " << argv[0] << " material thickness" << std::endl;
    std::cerr << "Example: " << argv[0] << " G4_lAr" << std::endl;
    std::cerr << "Example materials: G4_lAr, G4_Fe" << std::endl;
    return 1;
  }

  std::string material = argv[1];
  double thickness = std::stod(argv[2]);

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
      new MyDetectorConstruction(material.c_str(), thickness * mm));

  // Physics list
  G4VModularPhysicsList *physicsList = new FTFP_BERT();

  // G4StepLimiterPhysics *stepLimitPhys = new G4StepLimiterPhysics();
  // physicsList->RegisterPhysics(stepLimitPhys);

  runManager->SetUserInitialization(physicsList);

  // User action initialization
  runManager->SetUserInitialization(new MyLogActionInitialization());

  G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

  std::string filename = "logscale_mom_";
  if (material == "G4_lAr") {
    filename += "lar";
  } else if (material == "G4_Fe") {
    filename += "fe";
  } else {
    filename += material;
  }
  filename += "_" + std::to_string(static_cast<int>(thickness)) + "mm";
  filename += ".root";
  analysisManager->OpenFile(filename);

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

  analysisManager->Write();
  analysisManager->CloseFile();

  // Job termination
  // Free the store: user actions, physics_list and detector_description are
  // owned and deleted by the run manager, so they should not be deleted
  // in the main() program !

  delete runManager;
}

#include "MyActionInitialization.hpp"
#include "MyDetectorConstruction.hpp"

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
  // Define UI session
  //
  G4UIExecutive *ui = new G4UIExecutive(argc, argv);

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
      new MyDetectorConstruction("G4_lAr", 1 * m));

  // Physics list
  G4VModularPhysicsList *physicsList = new FTFP_BERT_ATL;

  G4StepLimiterPhysics *stepLimitPhys = new G4StepLimiterPhysics();
  physicsList->RegisterPhysics(stepLimitPhys);

  runManager->SetUserInitialization(physicsList);

  // User action initialization
  runManager->SetUserInitialization(new MyActionInitialization());

  // Initialize visualization
  //
  G4VisManager *visManager = new G4VisExecutive();
  // G4VisExecutive can take a verbosity argument - see /vis/verbose guidance.
  // G4VisManager* visManager = new G4VisExecutive("Quiet");
  visManager->Initialize();

  // Get the pointer to the User Interface manager
  G4UImanager *UImanager = G4UImanager::GetUIpointer();

  G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

  analysisManager->OpenFile("chart_visualisation.root");

  // runManager->SetVerboseLevel(2);
  // G4EventManager::GetEventManager()->SetVerboseLevel(2);
  // G4EventManager::GetEventManager()->GetTrackingManager()->SetVerboseLevel(2);
  // G4EventManager::GetEventManager()->GetStackManager()->SetVerboseLevel(2);

  // Start UI session
  // interactive mode
  UImanager->ApplyCommand("/control/execute init_vis.mac");
  UImanager->ApplyCommand("/control/execute run.mac");
  ui->SessionStart();
  delete ui;

  // Job termination
  // Free the store: user actions, physics_list and detector_description are
  // owned and deleted by the run manager, so they should not be deleted
  // in the main() program !

  delete visManager;
  delete runManager;
}

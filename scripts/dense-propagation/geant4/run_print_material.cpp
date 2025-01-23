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
  // Get nist material manager
  G4NistManager *nist = G4NistManager::Instance();

  G4Material *calo_mat = nist->FindOrBuildMaterial(argv[1]);

  std::cout << std::fixed << std::setprecision(13);
  std::cout << "x0: " << calo_mat->GetRadlen() << std::endl;
  std::cout << "l0: " << calo_mat->GetNuclearInterLength() << std::endl;
  std::cout << "ar: " << calo_mat->GetElement(0)->GetN() << std::endl;
  std::cout << "z: " << calo_mat->GetZ() << std::endl;
  std::cout << "massRho: " << calo_mat->GetDensity() / (g / cm3) << std::endl;
  std::cout << "electronDensity: " << calo_mat->GetElectronDensity() / (1 / cm3)
            << std::endl;
}

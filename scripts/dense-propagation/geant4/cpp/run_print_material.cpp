#include "CLHEP/Units/SystemOfUnits.h"
#include "G4NistManager.hh"

int main(int argc, char **argv) {
  // Get nist material manager
  G4NistManager *nist = G4NistManager::Instance();

  G4Material *calo_mat = nist->FindOrBuildMaterial(argv[1]);

  std::cout << std::fixed << std::setprecision(13);
  std::cout << "x0: " << calo_mat->GetRadlen() << std::endl;
  std::cout << "l0: " << calo_mat->GetNuclearInterLength() << std::endl;
  std::cout << "ar: " << calo_mat->GetElement(0)->GetN() << std::endl;
  std::cout << "z: " << calo_mat->GetZ() << std::endl;
  std::cout << "massRho: " << calo_mat->GetDensity() / (CLHEP::g / CLHEP::cm3)
            << std::endl;
  std::cout << "electronDensity: "
            << calo_mat->GetElectronDensity() / (1 / CLHEP::cm3) << std::endl;
}

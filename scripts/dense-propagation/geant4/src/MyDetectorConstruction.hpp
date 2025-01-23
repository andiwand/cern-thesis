#ifndef MyDetectorConstruction_h
#define MyDetectorConstruction_h 1

#include "MySensitiveDetector.hpp"

#include "G4Box.hh"
#include "G4Cons.hh"
#include "G4LogicalVolume.hh"
#include "G4NistManager.hh"
#include "G4Orb.hh"
#include "G4PVPlacement.hh"
#include "G4RunManager.hh"
#include "G4SDManager.hh"
#include "G4Sphere.hh"
#include "G4SystemOfUnits.hh"
#include "G4Trd.hh"
#include "G4UserLimits.hh"
#include "G4VUserDetectorConstruction.hh"
#include "globals.hh"

class MyDetectorConstruction : public G4VUserDetectorConstruction {
public:
  MyDetectorConstruction(std::string material, double thickness)
      : m_material{std::move(material)}, m_thickness(thickness) {}

  ~MyDetectorConstruction() override = default;

  G4VPhysicalVolume *Construct() override {
    // Get nist material manager
    G4NistManager *nist = G4NistManager::Instance();

    // Option to switch on/off checking of volumes overlaps
    //
    G4bool check_overlaps = true;

    //
    // World
    //
    G4double world_size_x = 4 * m;
    G4double world_size_yz = 2 * m;
    G4Material *world_mat = nist->FindOrBuildMaterial("G4_Galactic");

    auto solid_world = new G4Box("World", // its name
                                 0.5 * world_size_x, 0.5 * world_size_yz,
                                 0.5 * world_size_yz); // its size

    auto logic_world = new G4LogicalVolume(solid_world, // its solid
                                           world_mat,   // its material
                                           "World");    // its name

    auto phys_world = new G4PVPlacement(nullptr,         // no rotation
                                        G4ThreeVector(), // at (0,0,0)
                                        logic_world,     // its logical volume
                                        "World",         // its name
                                        nullptr,         // its mother  volume
                                        false,           // no boolean operation
                                        0,               // copy number
                                        check_overlaps); // overlaps checking

    //
    // Calo
    //
    G4double calo_size_xyz = m_thickness;
    int calo_slices = 1;
    G4double calo_slice_size_x = calo_size_xyz / calo_slices;
    G4ThreeVector calo_pos = G4ThreeVector(0, 0, 0);
    G4Material *calo_mat = nist->FindOrBuildMaterial(m_material.c_str());

    std::cout << std::fixed << std::setprecision(13);
    std::cout << "hi x0: " << calo_mat->GetRadlen() << std::endl;
    std::cout << "hi l0: " << calo_mat->GetNuclearInterLength() << std::endl;
    std::cout << "hi ar: " << calo_mat->GetElement(0)->GetN() << std::endl;
    std::cout << "hi z: " << calo_mat->GetZ() << std::endl;
    std::cout << "hi massRho: " << calo_mat->GetDensity() / (g / cm3)
              << std::endl;
    std::cout << "hi electronDensity: "
              << calo_mat->GetElectronDensity() / (1 / cm3) << std::endl;

    for (int i = 0; i < calo_slices; i++) {
      G4ThreeVector calo_slice_pos =
          calo_pos +
          G4ThreeVector(-calo_size_xyz * 0.5 + calo_slice_size_x * (i + 0.5), 0,
                        0);

      auto solid_calo_slice =
          new G4Box("calo_slice", 0.5 * calo_slice_size_x, 0.5 * calo_size_xyz,
                    0.5 * calo_size_xyz);

      auto logic_calo_slice = new G4LogicalVolume(solid_calo_slice, // its solid
                                                  calo_mat,     // its material
                                                  "CaloSlice"); // its name

      G4UserLimits *user_limits = new G4UserLimits();
      user_limits->SetMaxAllowedStep(1 * mm);
      logic_calo_slice->SetUserLimits(user_limits);

      new G4PVPlacement(nullptr,          // no rotation
                        calo_slice_pos,   // at position
                        logic_calo_slice, // its logical volume
                        "CaloSlice",      // its name
                        logic_world,      // its mother  volume
                        false,            // no boolean operation
                        i,                // copy number
                        check_overlaps);  // overlaps checking
    }

    //
    // Screen
    //
    G4double screen_size_x = 1 * um;
    G4double screen_size_yz = 1 * m;
    G4ThreeVector screen_pos =
        G4ThreeVector(1.5 * m + screen_size_x / 2., 0, 0);
    G4Material *screen_mat = nist->FindOrBuildMaterial("G4_Si");

    auto solid_screen = new G4Box("screen",            // its name
                                  0.5 * screen_size_x, // its size
                                  0.5 * screen_size_yz, 0.5 * screen_size_yz);

    logic_screen = new G4LogicalVolume(solid_screen, // its solid
                                       screen_mat,   // its material
                                       "Screen");    // its name

    new G4PVPlacement(nullptr,         // no rotation
                      screen_pos,      // at position
                      logic_screen,    // its logical volume
                      "Screen",        // its name
                      logic_world,     // its mother  volume
                      false,           // no boolean operation
                      0,               // copy number
                      check_overlaps); // overlaps checking

    //
    // always return the physical World
    //
    return phys_world;
  }

  void ConstructSDandField() override {
    G4SDManager *sd_man = G4SDManager::GetSDMpointer();

    MySensitiveDetector *sensitive = new MySensitiveDetector("Sensitive");
    SetSensitiveDetector("Screen", sensitive, true);
    sd_man->AddNewDetector(sensitive);
    logic_screen->SetSensitiveDetector(sensitive);
  }

protected:
  G4LogicalVolume *logic_screen{};

private:
  std::string m_material;
  double m_thickness{};
};

#endif

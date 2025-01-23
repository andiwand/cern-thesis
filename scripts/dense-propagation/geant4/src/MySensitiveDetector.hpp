#ifndef MySensitiveDetector_h
#define MySensitiveDetector_h 1

#include "MyTrackerHit.hpp"

#include "G4AnalysisManager.hh"
#include "G4PrimaryParticle.hh"
#include "G4SDManager.hh"
#include "G4VSensitiveDetector.hh"

class G4Run;

class MySensitiveDetector : public G4VSensitiveDetector {
public:
  MySensitiveDetector(G4String name) : G4VSensitiveDetector(name) {
    collectionName.insert("hits");
  }

  ~MySensitiveDetector() override = default;

  G4bool ProcessHits(G4Step *aStep, G4TouchableHistory *ROhist) override {
    double edep = aStep->GetTotalEnergyDeposit();

    auto newHit = new TrackerHit();

    newHit->SetTrackID(aStep->GetTrack()->GetTrackID());
    newHit->SetChamberNb(
        aStep->GetPreStepPoint()->GetTouchableHandle()->GetCopyNumber());
    newHit->SetEdep(edep);
    newHit->SetPos(aStep->GetPostStepPoint()->GetPosition());

    fHitsCollection->insert(newHit);

    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

    int particle = aStep->GetTrack()->GetTrackID();
    G4PrimaryParticle *primaryParticle =
        aStep->GetTrack()->GetDynamicParticle()->GetPrimaryParticle();
    double x = aStep->GetPreStepPoint()->GetPosition().z();
    double y = aStep->GetPreStepPoint()->GetPosition().y();

    if (primaryParticle != nullptr) {
      double eloss = primaryParticle->GetKineticEnergy() -
                     aStep->GetTrack()->GetKineticEnergy();

      analysisManager->FillNtupleDColumn(0, particle);
      analysisManager->FillNtupleDColumn(1, x / CLHEP::mm);
      analysisManager->FillNtupleDColumn(2, y / CLHEP::mm);
      analysisManager->FillNtupleDColumn(3, eloss / CLHEP::GeV);
      analysisManager->FillNtupleDColumn(
          4, primaryParticle->GetKineticEnergy() / CLHEP::GeV);
      analysisManager->FillNtupleDColumn(
          5, aStep->GetTrack()->GetKineticEnergy() / CLHEP::GeV);
      analysisManager->AddNtupleRow();
    }

    return true;
  }

  void Initialize(G4HCofThisEvent *hce) override {
    fHitsCollection =
        new TrackerHitsCollection(SensitiveDetectorName, collectionName[0]);

    G4int hcID =
        G4SDManager::GetSDMpointer()->GetCollectionID(collectionName[0]);
    hce->AddHitsCollection(hcID, fHitsCollection);
  }

  void EndOfEvent(G4HCofThisEvent *hce) override {
    if (verboseLevel > 1) {
      G4int nofHits = fHitsCollection->entries();
      G4cout << G4endl << "-------->Hits Collection: in this event they are "
             << nofHits << " hits in the tracker chambers: " << G4endl;
      for (G4int i = 0; i < nofHits; i++)
        (*fHitsCollection)[i]->Print();
    }
  }

private:
  TrackerHitsCollection *fHitsCollection = nullptr;
};

#endif

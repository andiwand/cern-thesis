#pragma once

#include "MyTrackerHit.hpp"

#include "G4AnalysisManager.hh"
#include "G4Event.hh"
#include "G4PrimaryParticle.hh"
#include "G4RunManager.hh"
#include "G4SDManager.hh"
#include "G4VSensitiveDetector.hh"

#include <unordered_set>

class G4Run;

class MySensitiveDetector : public G4VSensitiveDetector {
public:
  explicit MySensitiveDetector(G4String name) : G4VSensitiveDetector(name) {
    collectionName.insert("hits");
  }

  G4bool ProcessHits(G4Step *aStep, G4TouchableHistory *ROhist) override {
    int particle = aStep->GetTrack()->GetTrackID();
    G4PrimaryParticle *primaryParticle =
        aStep->GetTrack()->GetDynamicParticle()->GetPrimaryParticle();
    double x = aStep->GetPreStepPoint()->GetPosition().z();
    double y = aStep->GetPreStepPoint()->GetPosition().y();
    double edep = aStep->GetTotalEnergyDeposit();

    if (primaryParticle == nullptr) {
      return false;
    }
    // A sensitive volume can take several steps for one track. Record the
    // first screen crossing once, using the state at the entrance plane.
    if (!m_recordedTracks.insert(particle).second) {
      return false;
    }

    auto newHit = new TrackerHit();

    newHit->SetTrackID(aStep->GetTrack()->GetTrackID());
    newHit->SetChamberNb(
        aStep->GetPreStepPoint()->GetTouchableHandle()->GetCopyNumber());
    newHit->SetEdep(edep);
    newHit->SetPos(aStep->GetPostStepPoint()->GetPosition());

    fHitsCollection->insert(newHit);

    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

    double p_initial = primaryParticle->GetTotalMomentum();
    double t_final = aStep->GetPreStepPoint()->GetGlobalTime();
    double p_final = aStep->GetPreStepPoint()->GetMomentum().mag();
    double eloss = primaryParticle->GetTotalEnergy() -
                   aStep->GetPreStepPoint()->GetTotalEnergy();
    G4ThreeVector direction =
        aStep->GetPreStepPoint()->GetMomentumDirection().unit();

    analysisManager->FillNtupleIColumn(1, 0, particle);
    analysisManager->FillNtupleDColumn(1, 1, p_initial / CLHEP::GeV);
    analysisManager->FillNtupleDColumn(1, 2, x / CLHEP::mm);
    analysisManager->FillNtupleDColumn(1, 3, y / CLHEP::mm);
    analysisManager->FillNtupleDColumn(1, 4,
                                       t_final / CLHEP::ns * 2.997925e+02);
    analysisManager->FillNtupleDColumn(1, 5, direction[0]);
    analysisManager->FillNtupleDColumn(1, 6, direction[1]);
    analysisManager->FillNtupleDColumn(1, 7, direction[2]);
    analysisManager->FillNtupleDColumn(1, 8, p_final / CLHEP::GeV);
    analysisManager->FillNtupleDColumn(1, 9, eloss / CLHEP::GeV);
    analysisManager->FillNtupleDColumn(
        1, 10, primaryParticle->GetKineticEnergy() / CLHEP::GeV);
    analysisManager->FillNtupleDColumn(
        1, 11, aStep->GetPreStepPoint()->GetKineticEnergy() / CLHEP::GeV);
    analysisManager->FillNtupleIColumn(
        1, 12, G4RunManager::GetRunManager()->GetCurrentEvent()->GetEventID());
    analysisManager->AddNtupleRow(1);

    return true;
  }

  void Initialize(G4HCofThisEvent *hce) override {
    m_recordedTracks.clear();
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
  std::unordered_set<int> m_recordedTracks;
  TrackerHitsCollection *fHitsCollection = nullptr;
};

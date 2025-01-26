#pragma once

#include "G4AnalysisManager.hh"
#include "G4Run.hh"
#include "G4RunManager.hh"
#include "G4UserRunAction.hh"

class G4Run;

class MyRunAction : public G4UserRunAction {
public:
  MyRunAction() {}

  ~MyRunAction() override {}

  void BeginOfRunAction(const G4Run *run) override {
    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

    analysisManager->CreateNtuple("reading", "reading");
    analysisManager->CreateNtupleDColumn("particle");
    analysisManager->CreateNtupleDColumn("x");
    analysisManager->CreateNtupleDColumn("y");
    analysisManager->CreateNtupleDColumn("e_loss");
    analysisManager->CreateNtupleDColumn("e_init");
    analysisManager->CreateNtupleDColumn("e_final");
    analysisManager->FinishNtuple();
  }

  void EndOfRunAction(const G4Run *run) override {
    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

    analysisManager->Write();
    analysisManager->CloseFile();
  }

private:
};

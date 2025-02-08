#pragma once

#include "G4AnalysisManager.hh"
#include "G4Run.hh"
#include "G4RunManager.hh"
#include "G4UserRunAction.hh"

class G4Run;

class MyRunAction : public G4UserRunAction {
public:
  explicit MyRunAction(std::string output_file)
      : m_output_file(std::move(output_file)) {}

  void BeginOfRunAction(const G4Run *run) override {
    if (m_output_file.empty()) {
      return;
    }

    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();
    analysisManager->SetVerboseLevel(1);
    analysisManager->SetNtupleMerging(true);

    analysisManager->OpenFile(m_output_file);

    analysisManager->CreateNtuple("meta", "meta");
    analysisManager->CreateNtupleIColumn(0, "event");
    analysisManager->CreateNtupleIColumn(0, "trajectories");
    analysisManager->FinishNtuple(0);

    analysisManager->CreateNtuple("reading", "reading");
    analysisManager->CreateNtupleIColumn(1, "particle");
    analysisManager->CreateNtupleDColumn(1, "p_initial");
    analysisManager->CreateNtupleDColumn(1, "x");
    analysisManager->CreateNtupleDColumn(1, "y");
    analysisManager->CreateNtupleDColumn(1, "t");
    analysisManager->CreateNtupleDColumn(1, "dir0");
    analysisManager->CreateNtupleDColumn(1, "dir1");
    analysisManager->CreateNtupleDColumn(1, "dir2");
    analysisManager->CreateNtupleDColumn(1, "p_final");
    analysisManager->CreateNtupleDColumn(1, "e_loss");
    analysisManager->FinishNtuple(1);
  }

  void EndOfRunAction(const G4Run *run) override {
    if (m_output_file.empty()) {
      return;
    }

    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

    analysisManager->Write();
    analysisManager->CloseFile();
  }

private:
  std::string m_output_file;
};

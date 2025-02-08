#pragma once

#include "MyEventAction.hpp"
#include "MyLogPrimaryGeneratorAction.hpp"
#include "MyRunAction.hpp"
#include "MySteppingAction.hpp"

#include "G4VUserActionInitialization.hh"

#include <string>

class MyLogActionInitialization : public G4VUserActionInitialization {
public:
  explicit MyLogActionInitialization(std::string output_file)
      : m_output_file(std::move(output_file)) {}

  void BuildForMaster() const override {
    auto runAction = new MyRunAction(m_output_file);
    SetUserAction(runAction);
  }

  void Build() const override {
    SetUserAction(new MyLogPrimaryGeneratorAction());

    auto runAction = new MyRunAction(m_output_file);
    SetUserAction(runAction);

    auto eventAction = new MyEventAction();
    SetUserAction(eventAction);

    SetUserAction(new MySteppingAction(true));
  }

private:
  std::string m_output_file;
};

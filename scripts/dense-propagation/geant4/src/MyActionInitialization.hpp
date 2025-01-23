#ifndef MyActionInitialization_h
#define MyActionInitialization_h 1

#include "MyEventAction.hpp"
#include "MyPrimaryGeneratorAction.hpp"
#include "MyRunAction.hpp"
#include "MySteppingAction.hpp"

#include "G4VUserActionInitialization.hh"

class MyActionInitialization : public G4VUserActionInitialization {
public:
  MyActionInitialization() = default;

  ~MyActionInitialization() override = default;

  void BuildForMaster() const override {
    auto runAction = new MyRunAction();
    SetUserAction(runAction);
  }

  void Build() const override {
    SetUserAction(new MyPrimaryGeneratorAction());

    auto runAction = new MyRunAction();
    SetUserAction(runAction);

    auto eventAction = new MyEventAction();
    SetUserAction(eventAction);

    SetUserAction(new MySteppingAction());
  }
};

#endif

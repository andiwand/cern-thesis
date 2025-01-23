#ifndef MyLogActionInitialization_h
#define MyLogActionInitialization_h 1

#include "MyEventAction.hpp"
#include "MyLogPrimaryGeneratorAction.hpp"
#include "MyRunAction.hpp"
#include "MySteppingAction.hpp"

#include "G4VUserActionInitialization.hh"

class MyLogActionInitialization : public G4VUserActionInitialization {
public:
  MyLogActionInitialization() = default;

  ~MyLogActionInitialization() override = default;

  void BuildForMaster() const override {
    auto runAction = new MyRunAction();
    SetUserAction(runAction);
  }

  void Build() const override {
    SetUserAction(new MyLogPrimaryGeneratorAction());

    auto runAction = new MyRunAction();
    SetUserAction(runAction);

    auto eventAction = new MyEventAction();
    SetUserAction(eventAction);

    SetUserAction(new MySteppingAction());
  }
};

#endif

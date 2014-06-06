new Ajax.PeriodicalUpdater('dirtcount', '/dirt_count/', {
  method: 'get',
  frequency: 3,
  decay: 2,
});
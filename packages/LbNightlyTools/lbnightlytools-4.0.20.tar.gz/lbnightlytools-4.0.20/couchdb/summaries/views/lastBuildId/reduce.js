function(keys, values, rereduce) {
  if (rereduce) {
    return values.reduce(function(a, b) { return Math.max(a, b) }, -Infinity);
  } else {
    return Math.max.apply(null, values);
  }
}

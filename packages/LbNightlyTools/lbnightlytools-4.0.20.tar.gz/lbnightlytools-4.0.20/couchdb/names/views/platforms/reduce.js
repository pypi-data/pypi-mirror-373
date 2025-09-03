function(keys, values) {
  var max = "0000-00-00";
  values.forEach(function(value) {
    if (value  > max)
      max = value;
  });
  return max;
}

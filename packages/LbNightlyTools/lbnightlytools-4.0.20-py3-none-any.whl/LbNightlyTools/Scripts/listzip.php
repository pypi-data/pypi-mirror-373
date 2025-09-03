<?php
// return the list of files in a .zip file
header('Content-Type: text/html');

$zip_path = $_GET['zip'];
$zip_name = basename($zip_path);
$title = "Content of $zip_name";
?>
<!DOCTYPE html>
<html><head>
<title><?php echo $title; ?></title>
</head>
<body>
<?php
// drop '.zip' extension and add trailing '/'
$prefix = substr($zip_name, 0, strlen($zip_name) - 4) . '/';
$prefix_len = strlen($prefix);

$zip = new ZipArchive;
$res = $zip->open($zip_path);
if ($res === TRUE) {
  echo "<h1>$title</h1>\n";
  for ($i = 0; $i < $zip->numFiles; $i++) {
    $name = $zip->getNameIndex($i);
    if ($name == $prefix) continue;
    if (substr($name, 0, $prefix_len) == $prefix) {
      $entries[] = substr($zip->getNameIndex($i), $prefix_len);
    }
  }
  $zip->close();
  sort($entries);
  echo "<ul>\n";
  foreach ($entries as $value) {
    echo "<li><a href=\"$value\">$value</a></li>\n";
  }
  echo "</ul>\n";
} else {
  echo 'failure opening "' . $zip_name . '", code:' . $res;
}
?>
</body></html>

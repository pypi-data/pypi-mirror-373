<?php
$zip_name = $_GET['zip'];
$path = $_GET['path'];


if ( ! $zip_name || ! file_exists($zip_name) ) {
  header($_SERVER['SERVER_PROTOCOL'] . ' 404 Not Found', true, 404);
  echo "404 - Not Found";
  return;
}

switch(pathinfo($path, PATHINFO_EXTENSION)) {
  case 'css':  $ct = 'text/css';         break;
  case 'png':  $ct = 'image/png';        break;
  case 'gif':  $ct = 'image/gif';        break;
  case 'jpg':  $ct = 'image/jpeg';       break;
  case 'js':   $ct = 'text/javascript';  break;
  case 'svg':  $ct = 'image/svg+xml';    break;
  case 'json': $ct = 'application/json'; break;
  case 'html': $ct = 'text/html';        break;
  case 'htm':  $ct = 'text/html';        break;
  case 'gz':   $ct = 'application/x-gzip';        break;
  default:     $ct = 'text/plain';
}

# PHP < 5.4.5 (or < 5.3.15) has problems with zip files with more than 65535
# entries (issue in the version of libzip used, see
# https://libzip.org/news/release-0.10.html)
if (PHP_VERSION_ID >= 50405) {
  $zip = new ZipArchive();
  if ($zip->open($zip_name)) {
    $index = $zip->locateName($path);
    if ( $index === FALSE ) {
      header($_SERVER['SERVER_PROTOCOL'] . ' 404 Not Found', true, 404);
      echo "404 - Not Found";
    } else {
      header('Content-Type: ' . $ct);
      $content = $zip->getFromIndex($index);

      // If we are sending a gz, we need to add a few headers
      if ($ct == 'application/x-gzip'){
        header('Content-Encoding: gzip' );
        header('Accept-Ranges: bytes');

        // Since it is sent as a text,
        // remove the end of line char
        // Note: it might well be that we would need
        // to do this always, but it did not prove
        // necessary so far
        $content= rtrim($content, "\n");
        $contentLength = strlen($content);
        header("Content-Length: ".strlen($content));
        header("Content-Disposition: attachment; filename=".basename($path));
      }
      echo $content;
    }
    $zip->close();
  }
} else {
  // keep the output var to know the size of the file inside the archive
  exec('/usr/bin/unzip -qq -l "' . $zip_name . '" "' . $path. '"',
       $output, $return_var);
  if ( $return_var != 0 ) {
    header($_SERVER['SERVER_PROTOCOL'] . ' 404 Not Found', true, 404);
    echo "404 - Not Found";
  } else {

    header('Content-Type: ' . $ct);

    if ($ct == 'application/x-gzip'){
      // Specify a few headers.
      // We need to set the Content-Length manually
      // otherwise it is set one char too much because of the
      // EOL char.

      // output is of the form
      //     10685  02-28-2019 10:31   00000059/summaryGauss_00086576_00000059_1.xml.gz
      // We want the first element, which is the size
      $sizeArray = explode(" ", trim($output[0]));
      $size = $sizeArray[0];

      header('Content-Encoding: gzip' );
      header('Accept-Ranges: bytes');
      header("Content-Length: $size");
    }
    passthru('/usr/bin/unzip -p "' . $zip_name . '" "' . $path. '"');
  }
}
?>

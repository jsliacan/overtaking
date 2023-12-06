$folders = Get-ChildItem 'C:\Users\KatjaK\OneDrive - VTI/BikeLogs'

foreach($folder in $folders) {
    $env:name = $folder.Name
    $env:fullname = $folder.FullName
    $env:destinationData = "$env:userprofile/BL/Data/$env:name"

    New-Item -Path $env:destinationData -ItemType Directory
    Copy-Item -Path "$env:fullname/*" -Destination $env:destinationData -Exclude 'VariaVideo','pix' -Recurse
}
 $env:destinationMedia = "$env:userprofile/BL/Media/$env:name"
New-Item -Path $env:destinationMedia -ItemType Directory
Copy-Item -Path "$env:fullname/*" -Destination $env:destinationMedia -Include 'VariaVideo','pix' -Recurse
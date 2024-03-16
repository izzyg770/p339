import React from 'react';
import Pet from './Pet'; // Import the Pet component

const App = () => {
  // Define your pets data
  const petsData = [
    {
      name: 'Bacon Q Dog',
      likes: 'Belly rubs, playing tug-of-war, and sneaking onto the couch!',
      media: [
        { type: 'image', url: 'images/bacon/bacon.jpg', alt: 'Brown labradoodle wearing colorful lei' },
        // Add other media items for Bacon Q Dog
      ]
    },
    // Add data for other pets
  ];

  return (
    <div>
      {petsData.map((pet, index) => (
        <Pet key={index} name={pet.name} likes={pet.likes} media={pet.media} />
      ))}
    </div>
  );
};

export default App;
